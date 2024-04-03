#!/bin/bash
. /usr/share/beakerlib/beakerlib.sh || exit 1

rlJournalStart
	rlPhaseStartSetup
		rlRun "pushd data" 0 "Move to the data directory"
		rlRun "set -o pipefail"
	rlPhaseEnd

# Checks for good and full are identical
for type in good full; do
	rlPhaseStartTest "Check ${type} plans"
		rlRun -s "tmt lint plans --disable-check C000 --disable-check C001 /${type}" 0 "Check plan lint"
		rlAssertNotGrep "^warn:" $rlRun_LOG -E
		rlRun -s "tmt plans show /${type}" 0 "Get all /${type} plans"
		# Check schemas
#		rlAssertNotGrep "warn: .* is not valid under any of the given schemas" $rlRun_LOG -E
		# Check for any failing messages
		rlAssertNotGrep "fail:" $rlRun_LOG -E
		# Other catch all
#		rlAssertNotGrep "warn:" $rlRun_LOG
	rlPhaseEnd
done

	rlPhaseStartTest "Check failing plans"
		test="multiple-prepare"
		rlRun -s "tmt lint plans --enforce-check C000 --disable-check C001 /fail/${test}" 1 "Check plan lint: ${test}"
		# TODO: Add proper schema failure check here
		rlAssertGrep "fail C000 fmf node failed schema validation" $rlRun_LOG -E
		rlRun -s "tmt plans show /fail/${test}" 0 "Check plan failure in show"
		# Check schemas
		rlAssertGrep "warn: .* is not valid under any of the given schemas" $rlRun_LOG -E
		# Check specific failure message
		rlAssertGrep "fail: More than one CMake prepare step was specified" $rlRun_LOG -E

		test="discover-no-prepare"
		rlRun -s "tmt lint plans --enforce-check C000 --disable-check C001 /fail/${test}" 1 "Check plan lint: ${test}"
		# TODO: Add proper schema failure check here
		rlAssertGrep "fail C000 fmf node failed schema validation" $rlRun_LOG -E
		rlRun -s "tmt plans show /fail/${test}" 0 "Check plan failure in show"
		# Check schemas
		rlAssertGrep "warn: .* is not valid under any of the given schemas" $rlRun_LOG -E
		# Check specific failure message
		rlAssertGrep "fail: No CMake prepare step found" $rlRun_LOG -E
	rlPhaseEnd

	rlPhaseStartCleanup
		rlRun 'popd'
	rlPhaseEnd
rlJournalEnd
