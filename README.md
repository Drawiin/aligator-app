Personal diet and training app. Kotlin Multiplatform, generated from the
[Kotlin Multiplatform Wizard](https://kmp.jetbrains.com/) on 2026-10-08 with
Android, iOS, and “Do not share UI — Use SwiftUI”.

* [/androidApp](./androidApp) is the Android application entry point. It shows the Compose UI.
* [/sharedUI](./sharedUI) is that Compose UI. The wizard still uses this module name, and in this project it has an Android target only. iOS does not depend on it.
* [/iosApp](./iosApp/iosApp) is the SwiftUI application. It calls shared Kotlin through the `SharedLogic` framework.
* [/sharedLogic](./sharedLogic/src) is the shared Kotlin. The common code lives in [commonMain](./sharedLogic/src/commonMain/kotlin).

Cursor uses the harness in [`.ai/`](./.ai/) (system prompt, sub-agents, memory). The search CLIs are under [`library/tools/`](./library/tools/).

### Running the apps

Use the run configurations provided by the run widget in your IDE's toolbar. You can also use these commands and options:

- Android app: `./gradlew :androidApp:assembleDebug`
- iOS app: open the [/iosApp](./iosApp) directory in Xcode and run it from there.

### Running tests

Use the run button in your IDE's editor gutter, or run tests using Gradle tasks:

- Android tests: `./gradlew :sharedUI:testAndroidHostTest :sharedLogic:testAndroidHostTest`
- iOS tests: `./gradlew :sharedLogic:iosSimulatorArm64Test`

---

Learn more about [Kotlin Multiplatform](https://www.jetbrains.com/help/kotlin-multiplatform-dev/get-started.html)…