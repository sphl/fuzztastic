FROM ubuntu:24.04 AS fuzztastic-base

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        # Build tools
        build-essential \
        cmake \
        curl \
        git \
        libffi-dev \
        libssl-dev \
        pkg-config \
        software-properties-common \
        sudo \
        wget \
        # Python
        python3 \
        python3-dev \
        python3-pip \
        python3-venv \
        # LLVM and Clang
        clang-19 \
        clang-format \
        libc++-19-dev \
        libc++abi-19-dev \
        libzstd-dev \
        llvm-19 \
        llvm-19-dev \
        llvm-19-tools \
        zlib1g-dev \
        # FuzzTastic dependencies
        rapidjson-dev \
        # Utilities
        htop \
        tmux \
        vim

ENV POETRY_HOME="/opt/poetry"
ENV POETRY_CACHE_DIR="/tmp/poetry-cache"
ENV POETRY_NO_INTERACTION=1

RUN mkdir -p $POETRY_CACHE_DIR && \
    chmod 777 $POETRY_CACHE_DIR
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    chmod +x $POETRY_HOME/bin/poetry

ENV PATH="$POETRY_HOME/bin:$PATH"

RUN ln -sf /usr/bin/llvm-config-19 /usr/bin/llvm-config && \
    ln -sf /usr/bin/clang-19 /usr/bin/clang && \
    ln -sf /usr/bin/clang++-19 /usr/bin/clang++ && \
    ln -sf /usr/bin/opt-19 /usr/bin/opt && \
    ln -sf /usr/bin/llc-19 /usr/bin/llc

ENV LLVM_DIR="/usr/lib/llvm-19/lib/cmake/llvm"

ENV CC="/usr/bin/clang"
ENV CXX="/usr/bin/clang++"

ENV LD_LIBRARY_PATH="/fuzztastic/instrumentation/build/runtime-lib:$LD_LIBRARY_PATH"

RUN useradd -m -s /bin/bash user && \
    usermod -aG sudo user && \
    echo "user ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER user

WORKDIR /fuzztastic

FROM fuzztastic-base AS fuzztastic-dev

CMD ["sleep", "infinity"]

FROM fuzztastic-base AS fuzztastic

COPY --chown=user:user . .

RUN poetry install --without dev
RUN cd instrumentation && \
    mkdir -p build && \
    cd build && \
    cmake .. && \
    make -j

CMD ["/bin/bash"]
