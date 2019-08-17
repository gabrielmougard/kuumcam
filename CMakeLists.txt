cmake_minimum_required(VERSION 3.1)
#Setup our executable
add_executable( kuumcam src/kuumcam.cpp )
set(KUUMCAM_VENDOR "Kuumba software")

project( kuumcam )

#the version number
set ( kuumcam_VERSION_MAJOR 1)
set ( kuumcam_VERSION_MINOR 0)

#Register dependencies on header file
include_directories(include)

#Pass the compiler flags to cmake
set(CMAKE_C_FLAGS "-std=gnu99)
set(CMAKE_CXX_FLAGS "-std=c++17)

#Find openCV
find_package( OpenCV REQUIRED )

#Setup our libraries
find_path(AVCODEC_INCLUDE_DIR libavcodec/avcodec.h)
find_library(AVCODEC_LIBRARY avcodec)

find_path(SWSCALE_INCLUDE_DIR libswscale/swscale.h)
find_library(SWSCALE_LIBRARY swscale)

find_path(AVUTIL_INCLUDE_DIR libavutil/avutil.h)
find_library(AVUTIL_LIBRARY avutil)

target_include_directories( kuumcam PRIVATE ${AVCODEC_INCLUDE_DIR} ${SWSCALE_INCLUDE_DIR} ${AVUTIL_INCLUDE_DIR})
target_link_libraries( kuumcam PRIVATE ${AVCODEC_LIBRARY} ${SWSCALE_LIBRARY} ${AVUTIL_LIBRARY} ${OpenCV_LIBS})