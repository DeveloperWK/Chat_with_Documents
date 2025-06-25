# Maven Java Starter Project

This is a simple "Hello World" Java application built with Apache Maven. It serves as a basic template for starting a new Java project, demonstrating a standard project structure, dependency management, and build lifecycle with Maven.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- Java Development Kit (JDK) 1.8 or later
- Apache Maven

## Building the Project

To compile the source code, run the tests, and package the application into an executable JAR file, navigate to the project's root directory and run the following command:

```bash
mvn clean package
```

This command will perform the following steps:

1.  `clean`: Deletes the `target` directory to ensure a fresh build.
2.  `package`: Compiles the source code, runs any tests, and packages the compiled code into a JAR file.

Upon successful execution, you will find the JAR file at `target/my-app-1.0-SNAPSHOT.jar`.

## Running the Application

Once the project has been packaged, you can run the application from the command line:

```bash
java -cp target/my-app-1.0-SNAPSHOT.jar com.mycompany.app.App
```

You should see the following output in your console:

```
Hello World!
```

## Running Tests

To run the unit tests for the project without building the package, you can use the following Maven command:

```bash
mvn test
```

This will compile the test sources and run the tests using the Surefire Plugin.

## Project Structure

The project follows the standard Maven directory layout, which helps in keeping the project organized and easy to understand.

```
.
├── pom.xml                # Maven Project Object Model configuration
└── src
    ├── main
    │   └── java
    │       └── com
    │           └── mycompany
    │               └── app
    │                   └── App.java   # Main application class
    └── test
        └── java
            └── com
                └── mycompany
                    └── app
                        └── AppTest.java # Unit tests for the application
```
