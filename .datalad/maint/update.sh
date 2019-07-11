#!/bin/sh

set -e
set -u

salt_feed="http://longnow.org/projects/seminars/SALT.xml"
interval_feed="http://longnow.org/projects/seminars/interval.xml"
meta_update=".datalad/maint/update_metadata_from_feed.py"
importfeed="git annex importfeed --template \${feedtitle}/\${itempubdate}__\${itemtitle}\${extension} --force"

${importfeed} ${salt_feed}
${importfeed} ${interval_feed}
${meta_update} ${salt_feed}
${meta_update} ${interval_feed}
