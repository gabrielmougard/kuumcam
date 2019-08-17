#include <iostream>

#include "opencv2/opencv.hpp"
#include "opencv2/core.hpp"
#include "opencv2/imgproc.hpp"
#include "opencv2/dnn.hpp"

extern "C" {
    #include <libavcodec/avcodec.h>
    #include <libavutil/imgutils.h>
    #include <libswscale/swscale.h>
}



//#include "ctpl.h" //ThreadPool (https://github.com/vit-vit/CTPL)
#include "kuumcamConfig.h"
#include "ctpl.h"

using namespace cv;
using namespace cv::dnn;

const size_t inMatWidth = 300; //the exploited DL model is meant to be used with 300x300 images
const size_t inMatHeight = 300;
const double inScaleFactor = 1.0;
const float confidenceThreshold = 0.3;
const cv::Scalar meanVal(104.0,177.0,123.0);

#define CAFFE

// path to the pretrained models used for production
const std::string caffeConfigFile = "../models/deploy.prototxt";
const std::string caffeWeightFile = "../models/res10_300x300_ssd_iter_140000_fp16.caffemodel";
const std::string tensorflowConfigFile = "../models/opencv_face_detector.pbtxt";
const std::string tensorflowWeightFile = "../models/opencv_face_detector_uint8.pb";

/*
 * Face detection algorithm with a simple Gaussian blur on the box containing the face (for data anonymisation)
 */
void detectFaceDNN(Net network, Mat &inputFrame) {
    int inputFrameHeight = inputFrame.rows;
    int inputFrameWidth = inputFrame.cols;

#ifdef CAFFE
    cv::Mat inputBlob = cv::dnn::blobFromImage(inputFrame, inScaleFactor, cv::Size(inMatWidth,inMatHeight), meanVal, false, false);
#else
    cv::Mat inputBlob = cv::dnn::blobFromImage(inputFrame, inScaleFactor, cv::Size(inMatWidth, inMatHeight), meanVal, true, false);
#endif

    network.setInput(inputBlob, "data");
    cv::Mat detection = network.forward("detection_out");
    cv::Mat detectionMat(detection.size[2], detection.size[3], CV_32F, detection.ptr<float>());

    for (int i = 0; i < detectionMat.rows; i++) {
        float confidence = detectionMat.at<float>(i,2);
        //std::cout << confidence << std::endl;

        if (confidence > confidenceThreshold) { //get the coordinates of the bounding box
            int x1 = static_cast<int>(detectionMat.at<float>(i,3)*inputFrameWidth);
            int y1 = static_cast<int>(detectionMat.at<float>(i,4)*inputFrameHeight);
            int x2 = static_cast<int>(detectionMat.at<float>(i,5)*inputFrameWidth);
            int y2 = static_cast<int>(detectionMat.at<float>(i,6)*inputFrameHeight);

            int rectWidth = std::abs(x2-x1);
            int rectHeight = std::abs(y2-y1);

            //blurring for data anonymisation
            cv::Rect region(x1,y1,rectWidth,rectHeight);
            cv::GaussianBlur(inputFrame(region), inputFrame(region),Size(0,0),30);

            //TODO : get rid of this error : (it actually happens when a face is not completely in the camera FOV)
            //(-215:Assertion failed) 0 <= roi.x && 0 <= roi.width && roi.x + roi.width <= m.cols && 0 <= roi.y && 0 <= roi.height && roi.y + roi.height <= m.rows in function 'Mat'
            //
            // see this link : https://stackoverflow.com/questions/29712057/error-with-opencv-roi
        }
    }
}

/*
 * Convert a cv::Mat object into an AVFrame object with YUV420P format which is way lighter than BGR
 */
AVFrame* Mat2AVFrame(Mat &frame) { 

    cv::Size s = frame.size();
    int height = s.height;
    int width = s.width;

    //creating frame for conversion
    AVFrame *pFrameYUV = av_frame_alloc();
    AVFrame *pFrameBGR = av_frame_alloc();

    //Determine required buffer size and allocate buffer for YUV frame
    int numBytesYUV = av_image_get_buffer_size(AV_PIX_FMT_YUV420P,width,height,1);

    //assign image buffers
    avpicture_fill((AVPicture *)pFrameBGR, frame.data,AV_PIX_FMT_YUV420P,width,height);

    uint8_t* bufferYUV=(uint8_t *)av_malloc(numBytesYUV*sizeof(uint8_t));
    avpicture_fill((AVPicture *)pFrameYUV, bufferYUV, AV_PIX_FMT_YUV420P,width,height);

    //initialize Software scaling context
    struct SwsContext *sws_ctx = sws_getContext(width,
        height,
        AV_PIX_FMT_BGR24,width,
        height,
        AV_PIX_FMT_YUV420P,
        SWS_BILINEAR,
        NULL,
        NULL,
        NULL
    );

    // Convert the image from its BGR to YUV
    sws_scale(sws_ctx, (uint8_t const * const *)pFrameBGR->data,
        pFrameBGR->linesize,0,height,
        pFrameYUV->data,pFrameYUV->linesize);

    return pFrameYUV;
    
}

int main(int argc, char *argv[]) {
    fprintf(stdout,"%s Version %d.%d\n",
            argv[0],
            kuumcam_VERSION_MAJOR,
            kuumcam_VERSION_MINOR);
	std::cout << "Start capturing video ..." << std::endl;
#ifdef CAFFE
    Net network = cv::dnn::readNetFromCaffe(caffeConfigFile, caffeWeightFile);
    std::cout << "Caffe model loaded !" << std::endl;
#else
    Net network = cv::dnn::readNetFromTensorflow(tensorflowWeightFile, tensorflowConfigFile);
#endif

	VideoCapture cap(0); //open the default camera
    if (!cap.isOpened()) {
        return -1;
    }

    double tt_opencvDNN = 0;
    double fpsOpencvDNN = 0;
    namedWindow("kuum-cam render",1);
    for(;;) {
        Mat frame;
        cap >> frame; //get a new frame form the camera
        detectFaceDNN(network,frame);
        //imshow("kuum-cam render",frame); //for test only

        AVFrame* YUVframe = Mat2AVFrame(frame); //the YUV420P frame which we will exploit for VP8 encoding using FFmpeg API

        //test for YUV (trying to see the different planes of YUV)
        cv::Size s = frame.size();
        int height = s.height;
        int width = s.width;
        Mat MY = Mat(height,width,CV_8UC1);
        memcpy(MY.data,YUVframe->data[0], height*width);
        imshow("Test1",MY);
        Mat MU = Mat(height/2,width/2,CV_8UC1);
        memcpy(MU.data,YUVframe->data[1], height*width/4);
        imshow("Test2",MU);
        Mat MV = Mat(height/2,width/2,CV_8UC1);
        memcpy(MV.data,YUVframe->data[2], height*width/4);
        imshow("Test3",MV);
        //

        if (waitKey(30) >= 0) break;
    }
    // the camera will be deinitialized automatically in videoCapture destructor
}
