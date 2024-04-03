#!/bin/bash
. /usr/share/beakerlib/beakerlib.sh || exit 1

rlJournalStart
	rlPhaseStartSetup
		rlRun "pushd data" 0 "Move to the data directory"
		rlRun "set -o pipefail"
	rlPhaseEnd

	rlPhaseStartTest "Check plan"
		rlRun -s "tmt plans show plan"
	rlPhaseEnd

	rlPhaseStartCleanup
		rlRun 'popd'
	rlPhaseEnd
rlJournalEnd
