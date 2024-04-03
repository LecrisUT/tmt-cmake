#!/bin/bash
. /usr/share/beakerlib/beakerlib.sh || exit 1

rlJournalStart
	rlPhaseStartTest "Check plugin help messages"
		rlRun -s "tmt run prepare --how cmake --help" 0 "Check prepare help message"
	rlPhaseEnd
rlJournalEnd
