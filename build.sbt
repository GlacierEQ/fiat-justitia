ThisBuild / scalaVersion := "2.13.12"

lazy val root = (project in file("."))
  .settings(
    name := "tower-chisel-exhibits",
    version := "1.1.0",
    libraryDependencies += "org.chipsalliance" %% "chisel" % "6.6.0",
    addCompilerPlugin("org.chipsalliance" % "chisel-plugin" % "6.6.0" cross CrossVersion.full),
    Compile / unmanagedSourceDirectories += baseDirectory.value / "languages" / "chisel",
    Compile / run / fork := true
  )
