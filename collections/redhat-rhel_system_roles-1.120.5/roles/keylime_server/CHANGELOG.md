Changelog
=========

[1.2.4] - 2026-01-07
--------------------

### Other Changes

- refactor: handle INJECT_FACTS_AS_VARS=false by using ansible_facts instead (#107)

[1.2.3] - 2026-01-06
--------------------

### Other Changes

- ci: bump gha checkout from v5 to v6 (#101)
- ci: bump actions/checkout from 5 to 6 (#102)
- ci: add qemu tests for Fedora 43, drop Fedora 41 (#103)
- ci: bump actions/upload-artifact from 5 to 6 (#104)
- docs: fix copyright in license (#105)

[1.2.2] - 2025-11-17
--------------------

### Bug Fixes

- fix: cannot use community-general version 12 - no py27 and py36 support (#99)

### Other Changes

- ci: bump actions/checkout from 4 to 5 (#86)
- ci: rollout several recent changes to CI testing (#88)
- ci: support openSUSE Leap in qemu/kvm test matrix (#89)
- ci: use the new epel feature to enable EPEL for testing farm (#90)
- ci: use tox-lsr 3.12.0 for osbuild_config.yml feature (#92)
- ci: use JSON format for __bootc_validation (#93)
- ci: bump actions/github-script from 7 to 8 (#94)
- ci: bump actions/upload-artifact from 4 to 5 (#95)
- ci: use versioned upload-artifact instead of master; bump codeql-action to v4; bump upload-artifact to v5 (#96)
- ci: bump tox-lsr to 3.13.0 (#97)
- ci: bump tox-lsr to 3.14.0 - this moves standard-inventory-qcow2 to tox-lsr (#98)

[1.2.1] - 2025-08-01
--------------------

### Bug Fixes

- fix: Add SLES_16 var file with required packages and ensure pyasn1 (#84)

[1.2.0] - 2025-07-24
--------------------

### New Features

- feat: add openSUSE Leap 15.6 to integration test matrix (#82)

### Other Changes

- ci(packit): fix extra parameters for TF (#75)

[1.1.8] - 2025-07-02
--------------------

### Other Changes

- ci: ansible-plugin-scan is disabled for now (#63)
- ci: bump ansible-lint to v25; provide collection requirements for ansible-lint (#66)
- ci: Check spelling with codespell (#67)
- ci: Add test plan that runs CI tests and customize it for each role (#68)
- ci: In test plans, prefix all relate variables with SR_ (#69)
- ci: Fix bug with ARTIFACTS_URL after prefixing with SR_ (#70)
- ci: several changes related to new qemu test, ansible-lint, python versions, ubuntu versions (#71)
- ci: use tox-lsr 3.6.0; improve qemu test logging (#72)
- ci: skip storage scsi, nvme tests in github qemu ci (#73)
- ci: Bump sclorg/testing-farm-as-github-action from 3 to 4 (#74)
- ci: bump tox-lsr to 3.8.0; rename qemu/kvm tests (#76)
- ci: Add Fedora 42; use tox-lsr 3.9.0; use lsr-report-errors for qemu tests (#77)
- ci: Add support for bootc end-to-end validation tests (#78)
- ci: Use ansible 2.19 for fedora 42 testing; support python 3.13 (#79)
- refactor: support ansible 2.19 (#80)

[1.1.7] - 2025-01-09
--------------------

### Other Changes

- ci: Use Fedora 41, drop Fedora 39 (#60)
- ci: Use Fedora 41, drop Fedora 39 - part two (#61)

[1.1.6] - 2024-10-30
--------------------

### Other Changes

- ci: Add tft plan and workflow (#48)
- ci: Update fmf plan to add a separate job to prepare managed nodes (#50)
- ci: Bump sclorg/testing-farm-as-github-action from 2 to 3 (#51)
- ci: Add workflow for ci_test bad, use remote fmf plan (#52)
- ci: Fix missing slash in ARTIFACTS_URL (#53)
- ci: Add tags to TF workflow, allow more [citest bad] formats (#54)
- ci: ansible-test action now requires ansible-core version (#55)
- ci: add YAML header to github action workflow files (#56)
- refactor: Use vars/RedHat_N.yml symlink for CentOS, Rocky, Alma wherever possible (#58)

[1.1.5] - 2024-07-02
--------------------

### Bug Fixes

- fix: add support for EL10 (#46)

### Other Changes

- ci: ansible-lint action now requires absolute directory (#45)

[1.1.4] - 2024-06-11
--------------------

### Other Changes

- ci: Enable Packit CI for C10S (#39)
- ci: use tox-lsr 3.3.0 which uses ansible-test 2.17 (#40)
- ci: tox-lsr 3.4.0 - fix py27 tests; move other checks to py310 (#42)
- ci: Add supported_ansible_also to .ansible-lint (#43)

[1.1.3] - 2024-04-04
--------------------

### Other Changes

- ci: fix python unit test - copy pytest config to tests/unit (#35)
- ci: Bump ansible/ansible-lint from 6 to 24 (#36)
- ci: Bump mathieudutour/github-tag-action from 6.1 to 6.2 (#37)

[1.1.2] - 2024-01-16
--------------------

### Bug Fixes

- fix: add timeout for registrar service - use 30 second timeout for registrar and verifier

### Other Changes

- ci: support ansible-lint and ansible-test 2.16 (#31)
- ci: Use supported ansible-lint action; run ansible-lint against the collection (#32)

[1.1.1] - 2023-12-08
--------------------

### Other Changes

- ci: Bump actions/github-script from 6 to 7 (#28)
- refactor: get_ostree_data.sh use env shebang - remove from .sanity* (#29)

[1.1.0] - 2023-11-29
--------------------

### New Features

- feat: support for ostree systems (#24)

### Other Changes

- build(deps): Bump actions/checkout from 3 to 4 (#16)
- ci: ensure dependabot git commit message conforms to commitlint (#19)
- ci: tox-lsr version 3.1.1 (#23)
- ci: Use emulated TPM device on C9S (#25)

[1.0.1] - 2023-09-08
--------------------

### Other Changes

- ci: Add markdownlint, test_converting_readme, and build_docs workflows (#12)

  - markdownlint runs against README.md to avoid any issues with
    converting it to HTML
  - test_converting_readme converts README.md > HTML and uploads this test
    artifact to ensure that conversion works fine
  - build_docs converts README.md > HTML and pushes the result to the
    docs branch to publish dosc to GitHub pages site.
  - Fix markdown issues in README.md
  
  Signed-off-by: Sergei Petrosian <spetrosi@redhat.com>

- docs: Make badges consistent, run markdownlint on all .md files (#13)

  - Consistently generate badges for GH workflows in README RHELPLAN-146921
  - Run markdownlint on all .md files
  - Add custom-woke-action if not used already
  - Rename woke action to Woke for a pretty badge
  
  Signed-off-by: Sergei Petrosian <spetrosi@redhat.com>

- ci: Remove badges from README.md prior to converting to HTML (#14)

  - Remove thematic break after badges
  - Remove badges from README.md prior to converting to HTML
  
  Signed-off-by: Sergei Petrosian <spetrosi@redhat.com>

[1.0.0] - 2023-07-24
--------------------

### New Features

- New role for managing keylime server

  This is an ansible role for configuring and deploying the server
  components for Keylime Remote Attestation.
  
  It currently supports Fedora 36+, CentOS Stream 9.1+ and RHEL 9.1+
