pluginManagement {
    repositories {
        google {
            content {
                includeGroupByRegex("com\\.android.*")
                includeGroupByRegex("com\\.google.*")
                includeGroupByRegex("androidx.*")
            }
        }
        mavenCentral()
        gradlePluginPortal()  // 이 위치에서만 사용하도록 유지
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()  // 주로 Android 개발에 필요한 저장소
        mavenCentral()  // Maven 중앙 저장소
    }
}

rootProject.name = "treee"
include(":app")
