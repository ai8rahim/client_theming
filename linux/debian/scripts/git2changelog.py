#!//usr/bin/env python2.7

import subprocess
import re
import sys
import datetime

distribution="yakkety"

versionTagRE = re.compile("^v([0-9]+((\.[0-9]+)+))(-(.+))?$")

def collectEntries(baseCommit, baseVersion, kind):
    entries = []

    args = ["git", "log",
            "--format=%h%x09%an%x09%ae%x09%aD%x09%ad%x09%s",
            "--date=unix", "--author-date-order", "--reverse"]
    try:
        output = subprocess.check_output(args + [baseCommit + ".."])
    except:
        output = subprocess.check_output(args)

    for line in output.splitlines():
        (commit, name, email, date, revdate, subject) = line.split("\t")
        revdate = datetime.datetime.utcfromtimestamp(long(revdate)).strftime("%Y%m%d.%H%M%S")

        for tag in subprocess.check_output(["git", "tag",
                                            "--points-at",
                                            commit]).splitlines():
            m = versionTagRE.match(tag)
            if m:
                baseVersion = m.group(1)
                kind = "release" if m.group(4) is None else "beta"

        entries.append((commit, name, email, date, revdate, subject,
                        baseVersion, kind))

    entries.reverse()

    return entries

def genChangeLogEntries(f, entries, distribution):
    latestBaseVersion = None
    latestKind = None
    for (commit, name, email, date, revdate, subject, baseVersion, kind) in entries:
        if latestBaseVersion is None:
            latestBaseVersion = baseVersion
            latestKind = kind
        upstreamVersion = baseVersion + "-" + revdate
        if distribution=="stable":
            version = upstreamVersion
        else:
            version = upstreamVersion + "~" + distribution + "1"
        print >> f, "nextcloud-client (%s) %s; urgency=medium" % (version, distribution)
        print >> f
        print >> f, "  * " + subject
        print >> f
        print >> f, " -- %s <%s>  %s" % (name, email, date)
        print >> f
    return (latestBaseVersion, latestKind)

if __name__ == "__main__":
    distribution = sys.argv[2]

    #entries = collectEntries("8aade24147b5313f8241a8b42331442b7f40eef9", "2.2.4", "release")
    entries = collectEntries("dcac71898e7fda7ae4b149e2db25c178c90e7172", "2.3.1", "release")


    with open(sys.argv[1], "wt") as f:
        (baseVersion, kind) = genChangeLogEntries(f, entries, distribution)
        print baseVersion, kind
