FROM ubuntu:24.04 AS fuzztastic-base

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        # Build tools
        build-essential \
        cmake \
        curl \
        file \
        git \
        golang-go \
        libffi-dev \
        libssl-dev \
        pkg-config \
        software-properties-common \
        sudo \
        unzip \
        wget \
        # Python
        python3 \
        python3-dev \
        python3-pip \
        python3-venv \
        python-is-python3 \
        # LLVM and Clang
        clang-19 \
        clang-format-19 \
        clang-tidy-19 \
        libc++-19-dev \
        libc++abi-19-dev \
        libclang-rt-19-dev \
        libzstd-dev \
        llvm-19 \
        llvm-19-dev \
        llvm-19-tools \
        zlib1g-dev \
        # FuzzTastic dependencies
        rapidjson-dev \
        # Utilities
        htop \
        openssh-client \
        tmux \
        vim

ENV GOPATH="/opt/go"

RUN go install github.com/SRI-CSL/gllvm/cmd/...@latest

ENV PATH="$GOPATH/bin:$PATH"

ENV POETRY_HOME="/opt/poetry"
ENV POETRY_NO_INTERACTION=1

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    chmod +x $POETRY_HOME/bin/poetry

ENV PATH="$POETRY_HOME/bin:$PATH"

RUN ln -sf /usr/bin/clang-19 /usr/bin/clang && \
    ln -sf /usr/bin/clang-format-19 /usr/bin/clang-format && \
    ln -sf /usr/bin/clang-tidy-19 /usr/bin/clang-tidy && \
    ln -sf /usr/bin/clang++-19 /usr/bin/clang++ && \
    ln -sf /usr/bin/llc-19 /usr/bin/llc && \
    ln -sf /usr/bin/llvm-config-19 /usr/bin/llvm-config && \
    ln -sf /usr/bin/llvm-link-19 /usr/bin/llvm-link && \
    ln -sf /usr/bin/opt-19 /usr/bin/opt

ENV LLVM_DIR="/usr/lib/llvm-19/lib/cmake/llvm"

ENV CC="/usr/bin/clang"
ENV CXX="/usr/bin/clang++"

ENV FT_RUNTIME_LIB_DIR="/fuzztastic/instrumentation/build/runtime-lib"

ENV LD_LIBRARY_PATH="$FT_RUNTIME_LIB_DIR:$LD_LIBRARY_PATH"
ENV LIBRARY_PATH="$FT_RUNTIME_LIB_DIR:$LIBRARY_PATH"

RUN useradd -m -s /bin/bash user && \
    usermod -aG sudo user && \
    echo "user ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER user

WORKDIR /fuzztastic

FROM fuzztastic-base AS fuzztastic-dev

ENV CMAKE_BUILD_TYPE=Debug

CMD ["sleep", "infinity"]

FROM fuzztastic-base AS fuzztastic

COPY --chown=user:user . .

RUN poetry install --without dev
RUN cmake -B instrumentation/build -S instrumentation \
        -DCMAKE_BUILD_TYPE=Release && \
    cmake --build instrumentation/build --parallel

CMD ["/bin/bash"]
