# FFmpeg 5.1.6 - Exact version for audio service compatibility
FROM alpine:3.16

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

# Download and build FFmpeg 5.1.6
RUN curl -L https://ffmpeg.org/releases/ffmpeg-5.1.6.tar.xz -o ffmpeg-5.1.6.tar.xz && \
    tar -xf ffmpeg-5.1.6.tar.xz && \
    cd ffmpeg-5.1.6 && \
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
