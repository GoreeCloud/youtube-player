# iOS publishing safeguards (Development)

The GoreeCloud YouTube Player inherited iOS release scripts are disabled unless the explicit GOREECLOUD_IOS_STORE_PUBLISH_AUTHORIZED=1 switch is set. The Bun entrypoint and both Fastlane upload lanes fail closed. Submission for review, prior build rejection and automatic release are off by default.

This flag is not release approval. Approved Apple identity, signing, versioning, privacy and accessibility QA, native device tests, source-license compliance and owner-authorized promotion remain mandatory. No store uploads or device tests were performed.
