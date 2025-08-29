# FFmpeg 7.1.0 - Modern version for comparison
FROM alpine:3.18

# Install build dependencies
RUN apk add --no-cache \
    build-base \
    curl \
    tar \
    xz \
    yasm \
    nasm \
    pkgconfig \
    zlib-dev

# Create build directory
WORKDIR /ffmpeg_build

# Download and build FFmpeg 7.1.0
RUN curl -L https://ffmpeg.org/releases/ffmpeg-7.1.tar.xz -o ffmpeg-7.1.tar.xz && \
    tar -xf ffmpeg-7.1.tar.xz && \
    cd ffmpeg-7.1 && \
    ./configure \
        --prefix=/usr/local \
        --enable-gpl \
        --enable-small \
        --disable-debug \
        --disable-doc \
        --disable-ffplay \
        --disable-network \
        --disable-autodetect && \
    make -j$(nproc) && \
    make install && \
    cd / && \
    rm -rf /ffmpeg_build

# Set working directory for audio processing
WORKDIR /audio

# Default command
ENTRYPOINT ["ffmpeg"]
