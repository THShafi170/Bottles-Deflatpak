#!/bin/bash

SPEC_FILE="bottles.spec"
REQUIREMENTS_FILE="requirements.txt"
REQUIREMENTS_SPEC="requires.txt"
# Remove file(s) from previous run
[ -f ${REQUIREMENTS_SPEC} ] && rm -vf ${REQUIREMENTS_SPEC}
[ -f ${REQUIREMENTS_FILE} ] && rm -vf ${REQUIREMENTS_FILE}
# Make sure sources are present
spectool -gSf ${SPEC_FILE} 2>/dev/null
TARBALL="$(rpmspec --parse bottles.spec 2>/dev/null | grep Source0 | sed -r 's/^.*(Bottles.*)/\1/')"
TAR_REQ_FILE="$(tar tzf ${TARBALL} | grep ${REQUIREMENTS_FILE})"
tar -x ${TAR_REQ_FILE} --strip-components=1 -zf ${TARBALL}

# Remove version pinning from listed dependencies
# Require `requests`. The `use_chardet_on_py3` extra is not packaged in
# Fedora, but we have the required version of `chardet` present.
# Remove `wheel` from list - not a runtime requirement.
sed -r -i \
    -e 's/(^.*)==.*$/\1/g' \
    -e 's/(^requests)\[.*\]/\1/' \
    -e '/wheel/d' \
    requirements.txt

# Transform requirements for inclusion in spec file
for REQ in $(grep -v '^#' ${REQUIREMENTS_FILE}); do
    echo "Requires:       python3dist(${REQ@L})" >> ${REQUIREMENTS_SPEC}
done
