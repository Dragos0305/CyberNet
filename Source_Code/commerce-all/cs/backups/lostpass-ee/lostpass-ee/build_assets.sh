#!/bin/sh
BASE_DIR=$(dirname $(readlink -f $0));
echo ""
echo "basedir $BASE_DIR"
DST_DIR=$(readlink -f "$BASE_DIR/assets");
SRC_DIR=$(readlink -f "$BASE_DIR/src");

CSS="
index.scss:index.css
"

JS="
index.js:index.js
"

build_assets() {

    # build the css
    ARGUMENT=""
    for FILE in $CSS; do
        _IFS=$IFS; IFS=":";
        set -- $FILE; IFS=$_IFS;
        SRC="${SRC_DIR}/$1"; DST="${DST_DIR}/$2";
        echo "$SRC -> $DST"
        ARGUMENT="${ARGUMENT} ${SRC}:${DST}";
    done

    sass --trace --style=compressed --no-cache --sourcemap=none --stop-on-error ${ARGUMENT}

    # copy the javascript (no compression)
    for FILE in $JS; do
        _IFS=$IFS; IFS=":";
        set -- $FILE; IFS=$_IFS;
        SRC="${SRC_DIR}/$1"; DST="${DST_DIR}/$2";
        echo "$SRC -> $DST"
        /bin/cp "$SRC" "$DST"
    done
}

build_assets
