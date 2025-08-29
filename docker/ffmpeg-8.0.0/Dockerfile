# FFmpeg 8.0.0 - Latest version for comparison
FROM alpine:3.19

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

# Download and build FFmpeg 8.0.0
RUN curl -L https://ffmpeg.org/releases/ffmpeg-8.0.tar.xz -o ffmpeg-8.0.tar.xz && \
    tar -xf ffmpeg-8.0.tar.xz && \
    cd ffmpeg-8.0 && \
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
