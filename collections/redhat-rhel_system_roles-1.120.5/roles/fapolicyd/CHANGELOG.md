Changelog
=========

[1.1.12] - 2026-01-07
--------------------

### Other Changes

- ci: bump gha checkout from v5 to v6 (#85)
- ci: Bump actions/checkout from 5 to 6 (#86)
- ci: add qemu tests for Fedora 43, drop Fedora 41 (#87)
- ci: Bump actions/upload-artifact from 5 to 6 (#88)
- refactor: handle INJECT_FACTS_AS_VARS=false by using ansible_facts instead (#89)

[1.1.11] - 2025-11-17
--------------------

### Bug Fixes

- fix: cannot use community-general version 12 - no py27 and py36 support (#83)

### Other Changes

- ci: Bump actions/checkout from 4 to 5 (#70)
- ci: rollout several recent changes to CI testing (#72)
- ci: support openSUSE Leap in qemu/kvm test matrix (#73)
- ci: use the new epel feature to enable EPEL for testing farm (#74)
- ci: use tox-lsr 3.12.0 for osbuild_config.yml feature (#76)
- ci: use JSON format for __bootc_validation (#77)
- ci: Bump actions/github-script from 7 to 8 (#78)
- ci: Bump actions/upload-artifact from 4 to 5 (#79)
- ci: use versioned upload-artifact instead of master; bump codeql-action to v4; bump upload-artifact to v5 (#80)
- ci: bump tox-lsr to 3.13.0 (#81)
- ci: bump tox-lsr to 3.14.0 - this moves standard-inventory-qcow2 to tox-lsr (#82)

[1.1.10] - 2025-07-02
--------------------

### Other Changes

- ci: ansible-plugin-scan is disabled for now (#51)
- ci: bump ansible-lint to v25; provide collection requirements for ansible-lint (#54)
- ci: Check spelling with codespell (#55)
- ci: Add test plan that runs CI tests and customize it for each role (#56)
- ci: In test plans, prefix all relate variables with SR_ (#57)
- ci: Fix bug with ARTIFACTS_URL after prefixing with SR_ (#58)
- ci: several changes related to new qemu test, ansible-lint, python versions, ubuntu versions (#59)
- ci: use tox-lsr 3.6.0; improve qemu test logging (#60)
- ci: skip storage scsi, nvme tests in github qemu ci (#61)
- ci: Bump sclorg/testing-farm-as-github-action from 3 to 4 (#62)
- ci: bump tox-lsr to 3.8.0; rename qemu/kvm tests (#63)
- ci: Add Fedora 42; use tox-lsr 3.9.0; use lsr-report-errors for qemu tests (#64)
- ci: Add support for bootc end-to-end validation tests (#65)
- ci: Use ansible 2.19 for fedora 42 testing; support python 3.13 (#66)
- refactor: support ansible 2.19 (#67)

[1.1.9] - 2025-01-09
--------------------

### Other Changes

- ci: Use Fedora 41, drop Fedora 39 (#48)
- ci: Use Fedora 41, drop Fedora 39 - part two (#49)

[1.1.8] - 2024-10-30
--------------------

### Other Changes

- ci: ansible-test action now requires ansible-core version (#43)
- ci: add YAML header to github action workflow files (#44)
- refactor: Use vars/RedHat_N.yml symlink for CentOS, Rocky, Alma wherever possible (#46)

[1.1.7] - 2024-08-29
--------------------

### Bug Fixes

- fix: use journalctl -t fapolicyd to get fapolicyd log messages (#41)

### Other Changes

- ci: Add tags to TF workflow, allow more [citest bad] formats (#40)

[1.1.6] - 2024-08-21
--------------------

### Other Changes

- test: use ansible_python_interpreter (#38)

[1.1.5] - 2024-08-20
--------------------

### Other Changes

- ci: Add tft plan and workflow (#30)
- ci: Update fmf plan to add a separate job to prepare managed nodes (#32)
- ci: Bump sclorg/testing-farm-as-github-action from 2 to 3 (#33)
- ci: Add workflow for ci_test bad, use remote fmf plan (#34)
- ci: Fix missing slash in ARTIFACTS_URL (#35)
- test: make test_trusted_execution gather facts (#36)

[1.1.4] - 2024-07-02
--------------------

### Bug Fixes

- fix: add support for EL10 (#28)

### Other Changes

- ci: ansible-lint action now requires absolute directory (#27)

[1.1.3] - 2024-06-11
--------------------

### Other Changes

- ci: use tox-lsr 3.3.0 which uses ansible-test 2.17 (#22)
- ci: tox-lsr 3.4.0 - fix py27 tests; move other checks to py310 (#24)
- ci: Add supported_ansible_also to .ansible-lint (#25)

[1.1.2] - 2024-04-04
--------------------

### Other Changes

- ci: fix python unit test - copy pytest config to tests/unit (#15)
- ci: Bump ansible/ansible-lint from 6 to 24 (#18)
- test: Fix trusted test - use python script (#19)
- ci: Bump mathieudutour/github-tag-action from 6.1 to 6.2 (#20)

[1.1.1] - 2024-01-16
--------------------

### Other Changes

- ci: Use supported ansible-lint action; run ansible-lint against the collection (#12)
- ci: Use supported ansible-lint action; run ansible-lint against the collection (#13)

[1.1.0] - 2023-12-08
--------------------

### New Features

- feat: several role improvements (#8)

### Other Changes

- refactor: get_ostree_data.sh use env shebang - remove from .sanity* (#10)

[1.0.0] - 2023-11-27
--------------------

### New Features

- feat: New Role to manage fapolicyd
