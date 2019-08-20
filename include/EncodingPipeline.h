
extern "C" {
    #include <libavutil/avassert.h>
    #include <libavutil/channel_layout.h>
    #include <libavutil/opt.h>
    #include <libavutil/mathematics.h>
    #include <libavutil/timestamp.h>
    #include <libavformat/avformat.h>
    #include <libswscale/swscale.h>
    #include <libswresample/swresample.h>
}

int init_stream() {
    int ret;
    /* Initialize libavcodec, and register all the codecs and formats. */
    av_register_all();
    avformat_network_init();
    av_log_set_level(AV_LOG_DEBUG);

    /* allocate the output media context */
    avformat_alloc_output_context2(&oc,NULL,"rstp",filename);

    if (!oc) {
        std::cout<<"Could not read output from file extension: using MPEG."<< std::endl;
        avformat_alloc_output_context2(&oc, NULL, "mpeg", filename);
    }

    if (!oc){
      std::cout<<"Failed to ini output context"<< std::endl;
      return FAILED_OUTPUT_INIT;
    }
    
    fmt = oc->oformat;

    if(!fmt)
    {
      std::cout<<"Error creating outformat\n"<< std::endl;
    }

    /* Add the video streams using the default format codecs and initialize them */

    video_st = NULL;

    fmt->video_codec = CODEC_ID;
    std::cout<< "Codec = " << avcodec_get_name(fmt->video_codec) < video_codec != AV_CODEC_ID_NONE)
    {
      video_st = add_stream(oc, &video_codec, fmt->video_codec);
    }

    /* Now that all the parameters are set, we can open the video codecs and allocate the necessary encode buffers. */

    if (video_st) {
        open_video(oc, video_codec, video_st);
    }

    av_dump_format(oc, 0, filename, 1);
    char errorBuff[80];

    if (!(fmt->flags & AVFMT_NOFILE))
    {
      ret = avio_open(&oc->pb, filename, AVIO_FLAG_WRITE);
      if (ret < 0)
      {
        std::cout
        << "Could not open outfile: " << filename << "\n"
        << "Error:  " << av_make_error_string(errorBuff,80,ret) << "\n"
        << endl;
        
        return FAILED_OUTPUT;
      }
    }
    
    std::cout
    << "Stream: " << filename << "\n"
    << "format:  " << oc->oformat->name << "\n"
    << "vcodec:  " << video_codec->name << "\n"
    << "size:    " << dst_width << 'x' << dst_height << "\n"
    << "fps:     " << av_q2d(dst_fps) << "\n"
    << "pixfmt:  " << av_get_pix_fmt_name(video_st->codec->pix_fmt) << "\n"
    << endl;

    ret = avformat_write_header(oc,NULL);

    if (ret < 0) {
        std::cout
        << "Error occurred when writing header: " << av_make_error_string(errorBuff,80,ret) << "\n"
        << endl;
      
        return FAILED_OUTPUT_HEADER;
    }

    return 0
}

/*********************** CONFIGURE OUTPUT STREAM ************************/

AVStream *add_stream(AVFormatContext *oc, AVCodec **codec, enum AVCodecID codec_id) {
    AVCodecContext *c;
    AVStream *st;

    /* find the encoder */
    *codec = avcodec_find_encoder(codec_id);
    
    if (!(*codec))
    {
      std::cout << "Could not find encoder for" << avcodec_get_name(codec_id) << std::endl;
      exit(1);
    }

    st = avformat_new_stream(oc, *codec);

    if (!st) {
        std::cout << "Could not allocate stream" << std::endl;
        exit(1); 
    }

    st->id = oc->nb_streams-1;
    c = st->codec;

    c->codec_id = codec_id;
    c->bit_rate = 800000;
    /* Resolution must be a multiple of two. */
    c->width    = dst_width;
    c->height   = dst_height;

    /* timebase: This is the fundamental unit of time (in seconds) in terms
     * of which frame timestamps are represented. For fixed-fps content,
     * timebase should be 1/framerate and timestamp increments should be
     * identical to 1. 
     */
    c->time_base.den = STREAM_FRAME_RATE;
    c->time_base.num = 1;
    c->gop_size = 12; /* emit one intra frame every twelve frames at most */
    c->pix_fmt = STREAM_PIX_FMT;

    if (c->codec_id == AV_CODEC_ID_MPEG2VIDEO)
    {
      /* just for testing, we also add B frames */
      c->max_b_frames = 2;
    }
    
    if (c->codec_id == AV_CODEC_ID_MPEG1VIDEO)
    {
      /* Needed to avoid using macroblocks in which some coeffs overflow.
       * This does not happen with normal video, it just happens here as
       * the motion of the chroma plane does not match the luma plane. */
      c->mb_decision = 2;
    }
    
    /* Some formats want stream headers to be separate. */
    if (oc->oformat->flags & AVFMT_GLOBALHEADER)
    {
      c->flags |= CODEC_FLAG_GLOBAL_HEADER;
    }
    
    return st;
}

/*********************** OPEN OUTPUT CONNECTION ************************/
void open_video(AVFormatContext *oc, AVCodec *codec, AVStream *st) {
    int ret;
    AVCodecContext *c = st->codec;
    
    /* open the codec */
    AVDictionary *opts = NULL;
    
    /*
     Change options to trade off compression efficiency against encoding speed.
     If you specify a preset, the changes it makes will be applied before all other parameters are applied.
     You should generally set this option to the slowest you can bear.
     Values available: ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow, placebo.
     */
    av_dict_set(&opts, "preset", "superfast", 0);
    /*
     Tune options to further optimize them for your input content. If you specify a tuning,
     the changes will be applied after --preset but before all other parameters.
     If your source content matches one of the available tunings you can use this, otherwise leave unset.
     Values available: film, animation, grain, stillimage, psnr, ssim, fastdecode, zerolatency.
     */
    av_dict_set(&opts, "tune", "zerolatency", 0);
    
    /* open the codec */
    ret = avcodec_open2(c, codec, &opts);
    
    if (ret < 0)
    {
      std::cout << "Could not open video codec" << std::endl;
      exit(1);
    }
    
    /* allocate and init a re-usable frame */
    frame = av_frame_alloc();
    pFrameBGR =av_frame_alloc();
    
    if (!frame)
    {
      std::cout << "Could not allocate video frame" << std::endl;
      exit(1);
    }
    
    frame->format = c->pix_fmt;
    frame->width = c->width;
    frame->height = c->height;
}

/***************** WRITE VIDEO FRAMES  *****************/

void write_video_frame(AVFormatContext *oc, AVStream *st, int play)
  {
    int ret;
    AVCodecContext *c = st->codec;
    
    int numBytesYUV = av_image_get_buffer_size(STREAM_PIX_FMT, dst_width,dst_height,1);
    
    if(!bufferYUV)
    {
      bufferYUV = (uint8_t *)av_malloc(numBytesYUV*sizeof(uint8_t));
    }
    
    /* Assign image buffers */
    avpicture_fill((AVPicture *)pFrameBGR, image.data, AV_PIX_FMT_BGR24,
                   dst_width, dst_height);
    
    avpicture_fill((AVPicture *)frame, bufferYUV, STREAM_PIX_FMT, dst_width, dst_height);
    
    if (!sws_ctx)
    {
      /* Initialise Software scaling context */
      sws_ctx = sws_getContext(dst_width,
                               dst_height,
                               AV_PIX_FMT_BGR24,
                               dst_width,
                               dst_height,
                               STREAM_PIX_FMT,
                               SWS_BILINEAR,
                               NULL,
                               NULL,
                               NULL
                               );
    }
    
    /* Convert the image from its BGR to YUV */
    sws_scale(sws_ctx, (uint8_t const * const *)pFrameBGR->data,
              pFrameBGR->linesize, 0, dst_height,
              frame->data, frame->linesize);
    
    AVPacket pkt = { 0 };
    int got_packet;
    av_init_packet(&pkt);
    
    /* encode the image */
    frame->pts = frame_count;
    ret = avcodec_encode_video2(c, &pkt, play ? NULL : frame, &got_packet);
    
    if (ret < 0)
    {
      std::cout << "Error while encoding video frame" << std::endl;
      exit(1);
    }
    /* If size is zero, it means the image was buffered. */
    
    if (got_packet)
    {
      ret = write_frame(oc, &c->time_base, st, &pkt);
    }
    else
    {
      if (play)
        video_is_eof = 1;
      ret = 0;
    }
    
    if (ret < 0)
    {
      std::cout << "Error while writing video frame" << std::endl;
      exit(1);
    }
    
    frame_count++;
}

int write_frame(AVFormatContext *fmt_ctx, const AVRational *time_base, AVStream *st, AVPacket *pkt) {
        /* rescale output packet timestamp values from codec to stream timebase */
        pkt->pts = av_rescale_q_rnd(pkt->pts, *time_base, st->time_base, AVRounding(AV_ROUND_NEAR_INF|AV_ROUND_PASS_MINMAX));
        pkt->dts = av_rescale_q_rnd(pkt->dts, *time_base, st->time_base, AVRounding(AV_ROUND_NEAR_INF|AV_ROUND_PASS_MINMAX));
        pkt->duration = av_rescale_q(pkt->duration, *time_base, st->time_base);
        pkt->stream_index = st->index;
 
        /* Write the compressed frame to the media file. */
        return av_interleaved_write_frame(fmt_ctx, pkt);
}