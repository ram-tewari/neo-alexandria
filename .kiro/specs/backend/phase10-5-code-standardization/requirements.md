# Requirements Document

## Introduction

Phase 10.5 addresses critical technical debt and test failures across the Neo-Alexandria backend codebase. The system currently has 75 failing tests and 24 errors that prevent production readiness. This phase focuses on systematic code standardization, bug fixes, and implementing AI error prevention patterns to ensure all tests pass and the codebase follows established best practices.

The scope includes fixing model field inconsistencies, UUID serialization issues, SQLAlchemy query problems, pytest fixture usage, missing dependencies, regex errors, test assertion mismatches, async ingestion failures, database constraints, performance test thresholds, ML tensor errors, and API endpoint inconsistencies.

## Glossary

- **Test Suite**: The collection of automated tests in the backend/tests/ directory
- **Resource Model**: The primary SQLAlchemy model representing learning resources in app/models.py
- **Fixture**: A pytest mechanism for providing test data and setup through dependency injection
- **UUID Serialization**: The process of converting UUID objects to string format for JSON responses
- **EARS Pattern**: Easy Approach to Requirements Syntax - a structured format for writing requirements
- **SQLAlchemy ORM**: The Object-Relational Mapping library used for database operations
- **API Endpoint**: FastAPI route handlers in app/routers/ that handle HTTP requests
- **Model Field**: A column definition in a SQLAlchemy model class
- **Test Assertion**: A statement in a test that verifies expected behavior
- **Ingestion Pipeline**: The async process that processes and stores learning resources

## Requirements

### Requirement 1: Model Field Validation

**User Story:** As a developer, I want all model instantiations to use only valid fields defined in app/models.py, so that tests and application code don't fail with invalid keyword argument errors.

#### Acceptance Criteria

1. WHEN the Test Suite creates a Resource instance, THE Test Suite SHALL use only field names that exist in the Resource model definition in app/models.py
2. WHEN the Test Suite creates a TaxonomyNode instance, THE Test Suite SHALL use only field names that exist in the TaxonomyNode model definition in app/models.py
3. WHEN the Test Suite creates a Citation instance, THE Test Suite SHALL use only field names that exist in the Citation model definition in app/models.py
4. THE Test Suite SHALL NOT use the field name "summary" when creating Resource instances IF the Resource model does not define a "summary" field
5. THE Test Suite SHALL NOT use the field name "resource_type" when creating Resource instances IF the Resource model does not define a "resource_type" field

### Requirement 2: UUID Serialization

**User Story:** As an API consumer, I want all UUID values in JSON responses to be strings, so that the responses are valid JSON and can be parsed by clients.

#### Acceptance Criteria

1. WHEN an API Endpoint returns a response containing a UUID value, THE API Endpoint SHALL convert the UUID to a string using str()
2. WHEN an API Endpoint accepts a UUID parameter, THE API Endpoint SHALL accept the UUID as a string type
3. THE API Endpoint SHALL NOT return UUID objects directly in JSON response dictionaries
4. WHEN a Pydantic schema defines a UUID field, THE Pydantic schema SHALL use string type with validation rather than UUID type

### Requirement 3: SQLAlchemy Query Safety

**User Story:** As a developer, I want all database queries to use proper SQLAlchemy methods, so that queries execute without parameter binding errors.

#### Acceptance Criteria

1. WHEN an API Endpoint filters on a JSON field using a list value, THE API Endpoint SHALL use the contains() method for each list item rather than direct equality comparison
2. WHEN an API Endpoint filters on a regular field using multiple values, THE API Endpoint SHALL use the in_() method with the list of values
3. THE API Endpoint SHALL NOT use direct equality comparison (==) with Python list objects in SQLAlchemy filter() calls
4. THE API Endpoint SHALL use parameterized queries or ORM methods for all database operations

### Requirement 4: Pytest Fixture Usage

**User Story:** As a test developer, I want all tests to use fixtures through dependency injection, so that tests execute without fixture call errors.

#### Acceptance Criteria

1. WHEN a test function requires fixture data, THE test function SHALL declare the fixture name as a function parameter
2. THE Test Suite SHALL NOT call fixtures directly with parentheses like regular functions
3. WHEN a test requires a parameterized fixture, THE Test Suite SHALL use pytest.mark.parametrize with indirect=True
4. THE Test Suite SHALL access fixture data by referencing the parameter name without calling it

### Requirement 5: Dependency Management

**User Story:** As a developer, I want all required Python packages to be installed and available, so that imports succeed and tests can run.

#### Acceptance Criteria

1. WHEN the Test Suite imports a module, THE Test Suite SHALL only import modules that are listed in requirements.txt
2. WHEN the Test Suite requires an external API library, THE Test Suite SHALL mock the library calls rather than making real API requests
3. THE Test Suite SHALL include pytest skip markers for tests that require API keys when the API key is not available
4. THE requirements.txt file SHALL list all Python packages required by the application and test code

### Requirement 6: Regex Pattern Safety

**User Story:** As a developer, I want all regex patterns to be valid and properly escaped, so that regex operations execute without syntax errors.

#### Acceptance Criteria

1. WHEN code defines a regex pattern containing backslashes, THE code SHALL use raw string literals (r"pattern") or double-escaped backslashes
2. THE Test Suite SHALL validate regex patterns using re.compile() before using them in operations
3. THE Test Suite SHALL NOT use unescaped backslashes in regex pattern strings
4. WHEN a regex pattern fails to compile, THE code SHALL raise a clear error message indicating the invalid pattern

### Requirement 7: Test-API Consistency

**User Story:** As a test developer, I want test assertions to match actual API response structures, so that tests accurately verify API behavior.

#### Acceptance Criteria

1. WHEN a test verifies an API response, THE test SHALL assert against the actual response structure returned by the API Endpoint
2. THE Test Suite SHALL NOT assert against expected structures that differ from actual API implementations
3. WHEN an API Endpoint changes its response structure, THE Test Suite SHALL update corresponding test assertions to match
4. THE Test Suite SHALL verify API response structures by inspecting the actual endpoint implementation in app/routers/

### Requirement 8: Async Ingestion Reliability

**User Story:** As a system operator, I want the ingestion pipeline to handle errors gracefully, so that resource processing completes successfully or fails with clear error messages.

#### Acceptance Criteria

1. WHEN the Ingestion Pipeline processes a resource, THE Ingestion Pipeline SHALL wrap processing logic in try-except blocks
2. WHEN the Ingestion Pipeline encounters an error, THE Ingestion Pipeline SHALL set the resource status to "failed" and record the error message
3. WHEN the Ingestion Pipeline completes successfully, THE Ingestion Pipeline SHALL set the resource status to "completed"
4. THE Ingestion Pipeline SHALL log detailed error information including stack traces when processing fails
5. THE Ingestion Pipeline SHALL validate that required files exist before attempting to process them

### Requirement 9: Database Constraint Compliance

**User Story:** As a developer, I want all model instances to include required fields, so that database operations succeed without constraint violations.

#### Acceptance Criteria

1. WHEN code creates a TaxonomyNode instance, THE code SHALL provide values for all NOT NULL fields including id, name, slug, level, and path
2. WHEN code creates a Resource instance, THE code SHALL provide values for all NOT NULL fields including id, title, url, content_type, created_at, and updated_at
3. WHEN code creates a Citation instance, THE code SHALL provide values for all NOT NULL fields including id, resource_id, created_at, and updated_at
4. THE Test Suite SHALL use helper functions to generate required field values like slugs and paths when creating test data

### Requirement 10: Performance Test Realism

**User Story:** As a developer, I want performance test thresholds to reflect realistic system performance, so that tests pass when the system performs adequately.

#### Acceptance Criteria

1. WHEN a performance test measures operation duration, THE performance test SHALL use threshold values that reflect actual measured performance
2. THE Test Suite SHALL document the rationale for performance thresholds in comments when thresholds are adjusted
3. WHEN a performance test fails due to unrealistic thresholds, THE Test Suite SHALL profile the operation to determine realistic threshold values
4. THE Test Suite SHALL set performance thresholds with a reasonable margin above typical performance to account for system variance

### Requirement 11: ML Model Device Management

**User Story:** As a developer, I want ML models to be properly initialized on available devices, so that tensor operations execute without meta device errors.

#### Acceptance Criteria

1. WHEN code loads a pretrained ML model, THE code SHALL specify device_map="cpu" or device_map="auto" in the from_pretrained() call
2. WHEN code loads a pretrained ML model, THE code SHALL specify torch_dtype explicitly
3. THE Test Suite SHALL mock expensive ML model operations rather than loading real models
4. WHEN an ML model is loaded, THE code SHALL explicitly move the model to an available device using .to("cpu") or .to("cuda")

### Requirement 12: API Endpoint Status Codes

**User Story:** As an API consumer, I want endpoints to return correct HTTP status codes, so that I can properly handle success and error cases.

#### Acceptance Criteria

1. WHEN an API Endpoint receives a request for an existing resource, THE API Endpoint SHALL return HTTP status code 200
2. WHEN an API Endpoint receives a request for a non-existent resource, THE API Endpoint SHALL return HTTP status code 404
3. WHEN an API Endpoint validates resource existence, THE API Endpoint SHALL query the database to verify the resource exists before processing
4. THE API Endpoint SHALL NOT return 404 status codes for requests with valid resource identifiers that exist in the database

### Requirement 13: Security Best Practices

**User Story:** As a security-conscious developer, I want the codebase to follow security best practices, so that the application is protected against common vulnerabilities.

#### Acceptance Criteria

1. THE codebase SHALL NOT contain hardcoded secrets, API keys, or passwords
2. WHEN code requires configuration values, THE code SHALL load values from environment variables using os.getenv()
3. THE codebase SHALL use parameterized queries or ORM methods for all database operations
4. THE codebase SHALL validate and sanitize all user input using Pydantic schemas
5. THE codebase SHALL wrap all external API calls in try-except blocks for error handling

### Requirement 14: Code Quality Standards

**User Story:** As a developer, I want the codebase to follow consistent quality standards, so that code is maintainable and reliable.

#### Acceptance Criteria

1. THE codebase SHALL use only Python packages that are installed and listed in requirements.txt
2. THE codebase SHALL avoid N+1 query problems by using JOIN queries or filter with in_() method
3. THE Test Suite SHALL fix root causes of test failures rather than commenting out failing assertions
4. THE codebase SHALL include error handling for all operations that may fail
5. WHEN code makes non-obvious design decisions, THE code SHALL include comments explaining the rationale
