# Changelog

[PyPI History][1]

[1]: https://pypi.org/project/google-cloud-firestore/#history


## [1.7.0](https://www.github.com/googleapis/python-firestore/compare/v1.6.2...v1.7.0) (2020-05-18)


### Features

* Create CODEOWNERS ([#40](https://www.github.com/googleapis/python-firestore/issues/40)) ([a0cbf40](https://www.github.com/googleapis/python-firestore/commit/a0cbf403fe88f07c83bec81f275ac168be573e93))


### Bug Fixes

* **firestore:** fix get and getall method of transaction ([#16](https://www.github.com/googleapis/python-firestore/issues/16)) ([de3aca0](https://www.github.com/googleapis/python-firestore/commit/de3aca0e78b68f66eb76bc679c6e95b0746ad590))
* Update team to be in correct org ([#43](https://www.github.com/googleapis/python-firestore/issues/43)) ([bef5a3a](https://www.github.com/googleapis/python-firestore/commit/bef5a3af4613b5f9d753bb6f45275e480e4bb301))
* **firestore:** fix lint ([#48](https://www.github.com/googleapis/python-firestore/issues/48)) ([7fa00c4](https://www.github.com/googleapis/python-firestore/commit/7fa00c49dc3fab1d687fff9246f3e5ff0682cac0))

### [1.6.2](https://www.github.com/googleapis/python-firestore/compare/v1.6.1...v1.6.2) (2020-01-31)


### Bug Fixes

* update resume token for restarting BiDi streams ([#10282](https://www.github.com/googleapis/python-firestore/issues/10282)) ([61ec5a2](https://www.github.com/googleapis/python-firestore/commit/61ec5a2326aa101bbccbed229582570844e58bb7))

## 1.6.1

01-02-2020 10:35 PST


### Implementation Changes
- Recover watch streams on more error types ([#9995](https://github.com/googleapis/google-cloud-python/pull/9995))
- Simplify 'Collection.add' and avoid a spurious API call ([#9634](https://github.com/googleapis/google-cloud-python/pull/9634))

### Documentation
- Add new where operators to docstring ([#9789](https://github.com/googleapis/google-cloud-python/pull/9789))
- Change spacing in docs templates (via synth) ([#9750](https://github.com/googleapis/google-cloud-python/pull/9750))
- Add python 2 sunset banner to documentation ([#9036](https://github.com/googleapis/google-cloud-python/pull/9036))

## 1.6.0

11-06-2019 13:49 PST

### New Features
- Surface new 'IN' and 'ARRAY_CONTAINS_ANY' query operators. ([#9541](https://github.com/googleapis/google-cloud-python/pull/9541))

## 1.5.0

10-15-2019 06:45 PDT


### Implementation Changes
- Expand dotted keys in mappings used as cursors. ([#8568](https://github.com/googleapis/google-cloud-python/pull/8568))
- Tweak GAPIC client configuration (via synth). ([#9173](https://github.com/googleapis/google-cloud-python/pull/9173))

### New Features
- Add `IN`, `ARRAY_CONTAINS_ANY` operators; update docstrings (via synth). ([#9439](https://github.com/googleapis/google-cloud-python/pull/9439))
- Add `COLLECTION_GROUP` to `Index.QueryScope` enum; update docstrings (via synth). ([#9253](https://github.com/googleapis/google-cloud-python/pull/9253))
- Add `client_options` to v1 client. ([#9048](https://github.com/googleapis/google-cloud-python/pull/9048))

### Dependencies
- Pin 'google-cloud-core >= 1.0.3, < 2.0.0dev'. ([#9445](https://github.com/googleapis/google-cloud-python/pull/9445))

### Documentation
- Update README example to use non-deprecated `query.get`. ([#9235](https://github.com/googleapis/google-cloud-python/pull/9235))
- Remove duplicated word in README. ([#9297](https://github.com/googleapis/google-cloud-python/pull/9297))
- Fix intersphinx reference to `requests`. ([#9294](https://github.com/googleapis/google-cloud-python/pull/9294))
- Remove CI for gh-pages, use googleapis.dev for `api_core refs`. ([#9085](https://github.com/googleapis/google-cloud-python/pull/9085))
- Add license file. ([#9109](https://github.com/googleapis/google-cloud-python/pull/9109))
- Fix reference to library name ([#9047](https://github.com/googleapis/google-cloud-python/pull/9047))
- Remove compatability badges from READMEs. ([#9035](https://github.com/googleapis/google-cloud-python/pull/9035))

## 1.4.0

08-06-2019 11:43 PDT

### New Features
- Support emulator in client. ([#8721](https://github.com/googleapis/google-cloud-python/pull/8721))
- Add GAPIC client for Admin V1. ([#8667](https://github.com/googleapis/google-cloud-python/pull/8667))
- Add `Transaction.get` / `Transaction.get_all`. ([#8628](https://github.com/googleapis/google-cloud-python/pull/8628))

### Implementation Changes
- Remove send/recv msg size limit (via synth). ([#8955](https://github.com/googleapis/google-cloud-python/pull/8955))
- Deprecate `v1beta1` API / client. ([#8886](https://github.com/googleapis/google-cloud-python/pull/8886))
- Allow snapshot cursors from other collections for collection group queries. ([#8882](https://github.com/googleapis/google-cloud-python/pull/8882))
- Fix sorting `delete_changes` in `Watch._compute_snapshot`. ([#8809](https://github.com/googleapis/google-cloud-python/pull/8809))
- Treat `None` as EOF in `Watch.on_snapshot`. ([#8687](https://github.com/googleapis/google-cloud-python/pull/8687))
- Fix V1 `Client.collections` method. ([#8718](https://github.com/googleapis/google-cloud-python/pull/8718))
- Avoid adding `prefix` to update mask for transforms used in `update`. ([#8701](https://github.com/googleapis/google-cloud-python/pull/8701))
- Add `should_terminate` predicate for clean BiDi shutdown. ([#8650](https://github.com/googleapis/google-cloud-python/pull/8650))

### Dependencies
- Bump minimum version for google-api-core to 1.14.0. ([#8709](https://github.com/googleapis/google-cloud-python/pull/8709))

### Documentation
- Update intersphinx mapping for requests. ([#8805](https://github.com/googleapis/google-cloud-python/pull/8805))
- Link to googleapis.dev documentation in READMEs. ([#8705](https://github.com/googleapis/google-cloud-python/pull/8705))
- Add compatibility check badges to READMEs. ([#8288](https://github.com/googleapis/google-cloud-python/pull/8288))

### Internal / Testing Changes
- Preserve manual change in noxfile (run systests verbosely). ([#8744](https://github.com/googleapis/google-cloud-python/pull/8744))
- Update V1 conformance tests to match new repo / format. ([#8689](https://github.com/googleapis/google-cloud-python/pull/8689))
- Improve cleanups for `watch` system tests. ([#8638](https://github.com/googleapis/google-cloud-python/pull/8638))
- Avoid sharing top-level collection across test cases / CI runs. ([#8637](https://github.com/googleapis/google-cloud-python/pull/8637))

## 1.3.0

07-09-2019 13:19 PDT


### Implementation Changes
- Add missing transforms to 'google.cloud.firestore' shim. ([#8481](https://github.com/googleapis/google-cloud-python/pull/8481))
- Preserve reference to missing documents in 'Client.get_all'. ([#8472](https://github.com/googleapis/google-cloud-python/pull/8472))
- Add gRPC keepalive to gapic client initialization. ([#8264](https://github.com/googleapis/google-cloud-python/pull/8264))
- Add disclaimer to auto-generated template files. ([#8314](https://github.com/googleapis/google-cloud-python/pull/8314))
- Use correct environment variable to guard the 'system' part. ([#7912](https://github.com/googleapis/google-cloud-python/pull/7912))

### New Features
- Add 'client_options' support, update list method docstrings (via synth). ([#8509](https://github.com/googleapis/google-cloud-python/pull/8509))
- Allow kwargs to be passed to create_channel (via synth). ([#8390](https://github.com/googleapis/google-cloud-python/pull/8390))
- Add 'FieldPath.documentId()'. ([#8543](https://github.com/googleapis/google-cloud-python/pull/8543))

### Documentation
- Fix docstring example for 'Client.collection_group'. ([#8438](https://github.com/googleapis/google-cloud-python/pull/8438))
- Normalize docstring class refs. ([#8102](https://github.com/googleapis/google-cloud-python/pull/8102))

### Internal / Testing Changes
- Pin black version (via synth). ([#8583](https://github.com/googleapis/google-cloud-python/pull/8583))
- All: Add docs job to publish to googleapis.dev. ([#8464](https://github.com/googleapis/google-cloud-python/pull/8464))
- Declare encoding as utf-8 in pb2 files (via synth). ([#8352](https://github.com/googleapis/google-cloud-python/pull/8352))
- Suppress checking 'cov-fail-under' in nox default session (via synth).  ([#8241](https://github.com/googleapis/google-cloud-python/pull/8241))
- Blacken noxfile.py, setup.py (via synth). ([#8123](https://github.com/googleapis/google-cloud-python/pull/8123))
- Add empty lines (via synth). ([#8058](https://github.com/googleapis/google-cloud-python/pull/8058))

## 1.2.0

05-16-2019 12:25 PDT


### New Features
- Add support for numeric transforms: `increment` / `maximum` / `minimum`. ([#7989](https://github.com/googleapis/google-cloud-python/pull/7989))
- Add `client_info` support to V1 client. ([#7877](https://github.com/googleapis/google-cloud-python/pull/7877)) and ([#7898](https://github.com/googleapis/google-cloud-python/pull/7898))

### Dependencies
- Pin `google-cloud-core >= 1.0.0, < 2.0dev`. ([#7993](https://github.com/googleapis/google-cloud-python/pull/7993))

### Internal / Testing Changes
- Add nox session `docs`,  add routing header to method metadata, reorder methods (via synth).. ([#7771](https://github.com/googleapis/google-cloud-python/pull/7771))

## 1.1.0

04-30-2019 12:29 PDT


### New Features
- Add support for CollectionGroup queries. ([#7758](https://github.com/googleapis/google-cloud-python/pull/7758))

## 1.0.0

04-30-2019 10:00 PDT

### Implementation Changes
- Use parent path for watch on queries. ([#7752](https://github.com/googleapis/google-cloud-python/pull/7752))
- Add routing header to method metadata (via synth). ([#7749](https://github.com/googleapis/google-cloud-python/pull/7749))

## 0.32.1

04-05-2019 10:51 PDT


### Dependencies
- Update google-api-core dependency

## 0.32.0

04-01-2019 11:44 PDT


### Implementation Changes
- Allow passing metadata as part of creating a bidi ([#7514](https://github.com/googleapis/google-cloud-python/pull/7514))
- Remove classifier for Python 3.4 for end-of-life. ([#7535](https://github.com/googleapis/google-cloud-python/pull/7535))
- Rename 'Query.get' -> 'stream'. ([#7284](https://github.com/googleapis/google-cloud-python/pull/7284))
- Remove bogus error checking of query response stream. ([#7206](https://github.com/googleapis/google-cloud-python/pull/7206))
-'increment' / 'minimum' / 'maximum' field transform attributes. ([#7129](https://github.com/googleapis/google-cloud-python/pull/7129))
- Respect transform values passed into collection.add ([#7072](https://github.com/googleapis/google-cloud-python/pull/7072))
- Protoc-generated serialization update. ([#7083](https://github.com/googleapis/google-cloud-python/pull/7083))

### New Features
- Firestore: Add v1 API version. ([#7494](https://github.com/googleapis/google-cloud-python/pull/7494))
- Add 'Collection.list_documents' method. ([#7221](https://github.com/googleapis/google-cloud-python/pull/7221))
- Add 'DocumentReference.path' property. ([#7219](https://github.com/googleapis/google-cloud-python/pull/7219))

### Documentation
- Updated client library documentation URLs. ([#7307](https://github.com/googleapis/google-cloud-python/pull/7307))
- Fix the docstring example for 'Query.on_snapshot'.  ([#7281](https://github.com/googleapis/google-cloud-python/pull/7281))
- Update copyright headers

### Internal / Testing Changes
- Fix typo in proto comments (via synth).
- Prep firestore unit tests for generation from 'v1' protos. ([#7437](https://github.com/googleapis/google-cloud-python/pull/7437))
- Copy lintified proto files (via synth). ([#7466](https://github.com/googleapis/google-cloud-python/pull/7466))
- Add clarifying comment to blacken nox target. ([#7392](https://github.com/googleapis/google-cloud-python/pull/7392))
- Add protos as an artifact to library ([#7205](https://github.com/googleapis/google-cloud-python/pull/7205))

## 0.31.0

12-18-2018 11:20 PST


### Implementation Changes
- Implement equality semantics for public types ([#6916](https://github.com/googleapis/google-cloud-python/pull/6916))
- Pick up stub docstring fix in GAPIC generator. ([#6988](https://github.com/googleapis/google-cloud-python/pull/6988))
- Use 'DatetimeWithNanos' for converting timestamp messages. ([#6920](https://github.com/googleapis/google-cloud-python/pull/6920))
- Enable use of 'WriteBatch' as a context manager. ([#6912](https://github.com/googleapis/google-cloud-python/pull/6912))
- Document timeouts for 'Query.get' / 'Collection.get'. ([#6853](https://github.com/googleapis/google-cloud-python/pull/6853))
- Normalize FieldPath parsing / escaping ([#6904](https://github.com/googleapis/google-cloud-python/pull/6904))
- For queries ordered on `__name__`, expand field values to full paths. ([#6829](https://github.com/googleapis/google-cloud-python/pull/6829))
- Import `iam.policy` from `google.api_core`. ([#6741](https://github.com/googleapis/google-cloud-python/pull/6741))
- Prevent use of transforms as values passed to 'Query.where'. ([#6703](https://github.com/googleapis/google-cloud-python/pull/6703))
- 'Query.select([])' implies `__name__`. ([#6735](https://github.com/googleapis/google-cloud-python/pull/6735))
- Reject invalid paths passed to 'Query.{select,where,order_by}' ([#6770](https://github.com/googleapis/google-cloud-python/pull/6770))
- Prevent use of transforms as cursor values. ([#6706](https://github.com/googleapis/google-cloud-python/pull/6706))
- Refactor 'Document.get' to use the 'GetDocument' API. ([#6534](https://github.com/googleapis/google-cloud-python/pull/6534))
- Pick up enum fixes in the GAPIC generator. ([#6612](https://github.com/googleapis/google-cloud-python/pull/6612))
- Pick up changes to GAPIC client config. ([#6589](https://github.com/googleapis/google-cloud-python/pull/6589))
- Suppress deprecation warnings for 'assertRaisesRegexp'. ([#6543](https://github.com/googleapis/google-cloud-python/pull/6543))
- Firestore: pick up fixes to GAPIC generator. ([#6523](https://github.com/googleapis/google-cloud-python/pull/6523))
- Fix `client_info` bug, update docstrings. ([#6412](https://github.com/googleapis/google-cloud-python/pull/6412))
- Block calling 'DocumentRef.get()' with a single string. ([#6270](https://github.com/googleapis/google-cloud-python/pull/6270))

### New Features
- Impose required semantics for snapshots as cursors: ([#6837](https://github.com/googleapis/google-cloud-python/pull/6837))
- Make cursor-related 'Query' methods accept lists ([#6697](https://github.com/googleapis/google-cloud-python/pull/6697))
- Add 'Client.collections' method. ([#6650](https://github.com/googleapis/google-cloud-python/pull/6650))
- Add support for 'ArrayRemove' / 'ArrayUnion' transforms ([#6651](https://github.com/googleapis/google-cloud-python/pull/6651))
- Add support for `array_contains` query operator. ([#6481](https://github.com/googleapis/google-cloud-python/pull/6481))
- Add Watch Support ([#6191](https://github.com/googleapis/google-cloud-python/pull/6191))
- Remove use of deprecated 'channel' argument. ([#6271](https://github.com/googleapis/google-cloud-python/pull/6271))

### Dependencies
- Pin 'google-api_core >= 1.7.0'. ([#6937](https://github.com/googleapis/google-cloud-python/pull/6937))
- Update dependency to google-cloud-core ([#6835](https://github.com/googleapis/google-cloud-python/pull/6835))
- Bump minimum 'api_core' version for all GAPIC libs to 1.4.1. ([#6391](https://github.com/googleapis/google-cloud-python/pull/6391))

### Documentation
- Document Python 2 deprecation ([#6910](https://github.com/googleapis/google-cloud-python/pull/6910))
- Nnormalize docs for `page_size` / `max_results` / `page_token`. ([#6842](https://github.com/googleapis/google-cloud-python/pull/6842))
- Port changelog from 30.1 branch to master ([#6903](https://github.com/googleapis/google-cloud-python/pull/6903))
- Normalize use of support level badges ([#6159](https://github.com/googleapis/google-cloud-python/pull/6159))

### Internal / Testing Changes
- Add driver for listen conformance tests. ([#6935](https://github.com/googleapis/google-cloud-python/pull/6935))
- Add driver for query conformance tests. ([#6839](https://github.com/googleapis/google-cloud-python/pull/6839))
- Update noxfile.
- Blacken libraries ([#6794](https://github.com/googleapis/google-cloud-python/pull/6794))
- Omit local deps ([#6701](https://github.com/googleapis/google-cloud-python/pull/6701))
- Run black at end of synth.py ([#6698](https://github.com/googleapis/google-cloud-python/pull/6698))
- Add templates for flake8, coveragerc, noxfile, and black. ([#6642](https://github.com/googleapis/google-cloud-python/pull/6642))
- Fix delete conformance ([#6559](https://github.com/googleapis/google-cloud-python/pull/6559))
- Add synth metadata. ([#6567](https://github.com/googleapis/google-cloud-python/pull/6567))
- Refactor conformance tests. ([#6291](https://github.com/googleapis/google-cloud-python/pull/6291))
- Import stdlib ABCs from 'collections.abc' rather than 'collections'. ([#6451](https://github.com/googleapis/google-cloud-python/pull/6451))
- Fix path of tests-to-include in MANIFEST.in ([#6381](https://github.com/googleapis/google-cloud-python/pull/6381))
- Fix error from new flake8 version. ([#6320](https://github.com/googleapis/google-cloud-python/pull/6320))

## 0.30.1

12-11-2018 10:49 PDT
 

### Dependencies
- Update `core` and `api_core` dependencies to latest versions.

## 0.30.0

10-15-2018 09:04 PDT


### New Features
- Add `Document.collections` method. ([#5613](https://github.com/googleapis/google-cloud-python/pull/5613))
- Add `merge` as an option to `DocumentReference.set()` ([#4851](https://github.com/googleapis/google-cloud-python/pull/4851))
- Return emtpy snapshot instead of raising NotFound exception ([#5007](https://github.com/googleapis/google-cloud-python/pull/5007))
- Add Field path class ([#4392](https://github.com/googleapis/google-cloud-python/pull/4392))

### Implementation Changes
- Avoid overwriting `__module__` of messages from shared modules. ([#5364](https://github.com/googleapis/google-cloud-python/pull/5364))
- Don't omit originally-empty map values when processing timestamps. ([#6050](https://github.com/googleapis/google-cloud-python/pull/6050))

### Documentation
- Prep docs for repo split. ([#6000](https://github.com/googleapis/google-cloud-python/pull/6000))
- Docs: Replace links to `/stable/` with `/latest/`. ([#5901](https://github.com/googleapis/google-cloud-python/pull/5901))
- Document `FieldPath.from_string` ([#5121](https://github.com/googleapis/google-cloud-python/pull/5121))

### Internal / Testing Changes
- Use new Nox ([#6175](https://github.com/googleapis/google-cloud-python/pull/6175))
- Add new conformance tests. ([#6124](https://github.com/googleapis/google-cloud-python/pull/6124))
- Add `synth.py`. ([#6079](https://github.com/googleapis/google-cloud-python/pull/6079))
- Test document update w/ integer ids ([#5895](https://github.com/googleapis/google-cloud-python/pull/5895))
- Nox: use inplace installs ([#5865](https://github.com/googleapis/google-cloud-python/pull/5865))
- Re-sync with .proto / .textproto files from google-cloud-common. ([#5351](https://github.com/googleapis/google-cloud-python/pull/5351))
- Modify system tests to use prerelease versions of grpcio ([#5304](https://github.com/googleapis/google-cloud-python/pull/5304))
- Add test runs for Python 3.7 and remove 3.4 ([#5295](https://github.com/googleapis/google-cloud-python/pull/5295))
- Fix over-long line. ([#5129](https://github.com/googleapis/google-cloud-python/pull/5129))
- Distinguish `FieldPath` classes from field path strings ([#4466](https://github.com/googleapis/google-cloud-python/pull/4466))
- Fix bad trove classifier
- Cleanup `FieldPath` ([#4996](https://github.com/googleapis/google-cloud-python/pull/4996))
- Fix typo in `Document.collections` docstring. ([#5669](https://github.com/googleapis/google-cloud-python/pull/5669))
- Implement `FieldPath.__add__` ([#5149](https://github.com/googleapis/google-cloud-python/pull/5149))

## 0.29.0

### New features

- All non-simple field names are converted into unicode (#4859)

### Implementation changes

- The underlying generated code has been re-generated to pick up new features and bugfixes. (#4916)
- The `Admin` API interface has been temporarily removed.

### Dependencies

- Update dependency range for api-core to include v1.0.0 releases (#4944)
- The minimum version for `google-api-core` has been updated to version 1.0.0. This may cause some incompatibility with older google-cloud libraries, you will need to update those libraries if you have a dependency conflict. (#4944, #4946)

### Documentation

- Fixing "Fore" -> "For" typo in README docs. (#4317)

### Testing and internal changes

- Install local dependencies when running lint (#4936)
- Re-enable lint for tests, remove usage of pylint (#4921)
- Normalize all setup.py files (#4909)
- System test fix, changed ALREADY_EXISTS and MISSING_ENTITY to DOCUMENT_EXISTS and MISSING_DOCUMENT and updated wording (#4803)
- Cross-language tests (#4359)
- Fix import column lengths pass 79 (#4464)
- Making a `nox -s default` session for all packages. (#4324)
- Shorten test names (#4321)

## 0.28.0

### Documentation

- Added link to "Python Development Environment Setup Guide" in
  project README (#4187, h/t to @michaelawyu)

### Dependencies

- Upgrading to `google-cloud-core >= 0.28.0` and adding dependency
  on `google-api-core` (#4221, #4280)

PyPI: https://pypi.org/project/google-cloud-firestore/0.28.0/
