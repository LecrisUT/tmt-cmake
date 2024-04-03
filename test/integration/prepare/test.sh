#!/bin/bash
. /usr/share/beakerlib/beakerlib.sh || exit 1

rlJournalStart
	rlPhaseStartSetup
		rlRun "pushd data" 0 "Move to the data directory"
		rlRun "set -o pipefail"
	rlPhaseEnd

	# TODO: How to check for different provisions?
	rlPhaseStartTest "Run plans"
		rlRun "work_dir=${TMT_TEST_DATA}/tmt_root" 0 "Set predictable work_dir"
		rlRun -s "tmt run --id=\$work_dir -avvv plan --name default" 0 "Run plan default"
		rlAssertGrep "cmd: cmake -S$work_dir/default/tree -B$work_dir/default/data/build" $rlRun_LOG
		rlAssertGrep "out: -- Configuring done" $rlRun_LOG
		rlAssertGrep "out: -- Generating done" $rlRun_LOG
		rlAssertGrep "out: -- Build files have been written to: $work_dir/default/data/build" $rlRun_LOG
		rlAssertGrep "cmd: cmake --build $work_dir/default/data/build" $rlRun_LOG
		rlAssertGrep "out: dummy_target" $rlRun_LOG
		rlAssertGrep "out: Built target dummy" $rlRun_LOG
		rlAssertExists "$work_dir/default/data/build/CMakeCache.txt"
	rlPhaseEnd

	rlPhaseStartCleanup
		rlRun 'popd'
	rlPhaseEnd
rlJournalEnd
