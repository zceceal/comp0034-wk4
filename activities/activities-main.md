## Overview

This tutorial focuses on functional testing covering the Flask API routes.

Refer to the COMP0035 week 9 tutorial for:

- test naming convention
- using GIVEN-WHEN-THEN style syntax to specify a test
- Unit tests with pytest
- running pytest tests
- Pytest fixtures, including adding these to `conftest.py`
- using GitHub Actions to automatically run tests when code is pushed to GitHub
- coverage reporting
- using GitHub CoPilot or ChatGPT to write tests

## Setup the test environment

To do this you need to:

1. Install pytest
2. Create a tests directory and test files
3. Install your app code

### 1. Install pytest

Make sure you have installed pytest and selenium in your Python environment e.g.: `pip install pytest`

You may also need to configure your IDE to support running pytest tests, follow the relevant documentation:

- [Pycharm help: Testing frameworks](https://www.jetbrains.com/help/pycharm/testing-frameworks.html)
- [Python testing in VS Code](https://code.visualstudio.com/docs/python/testing)

### 2. Create a test folder and files

- Create a folder called `tests`. Refer to
  the [pytest documentation](https://docs.pytest.org/en/7.1.x/explanation/goodpractices.html#choosing-a-test-layout-import-rules)
  for alternate test directory structures.
- Create a Python test file in the `tests` folder called `test_routes.py`. You will add the tests to this.
- Create an empty Python file in the `tests` folder called `conftest.py`. You will add the fixtures to this.

### 3. Install your app code

This uses `pyproject.toml` which has metadata about your project code and how to configure pytest.

In the Terminal of your IDE, install the paralympics code using `pip install -e .`

Note: The `.` is part of the command and not a typo!

## Test the REST API routes using the Flask test client and pytest

To test the routes you will use a combination of:

- [Flask test client](https://flask.palletsprojects.com/en/3.0.x/testing/#fixtures) to create a running Flask app in a
  Pytest fixture
- [Pytest](https://docs.pytest.org/en/7.1.x/explanation/goodpractices.html#choosing-a-test-layout-import-rules) for test
  assertions

### Create a Flask test client as a pytest fixture

This is explained with code in the [Flask documentation](https://flask.palletsprojects.com/en/3.0.x/testing/#fixtures).

Add the following to `conftest.py`:

```python
import os
from pathlib import Path
import pytest
from paralympics import create_app


@pytest.fixture(scope='module')
def app():
    """Fixture that creates a test app.

    The app is created with test config parameters that include a temporary database. The app is created once for
    each test module.

    Returns:
        app A Flask app with a test config
    """
    # Location for the temporary testing database
    db_path = Path(__file__).parent.parent.joinpath('data', 'paralympics_testdb.sqlite')
    test_cfg = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + str(db_path),
    }
    app = create_app(test_config=test_cfg)

    yield app

    # clean up / reset resources
    # Delete the test database
    os.unlink(db_path)


@pytest.fixture()
def client(app):
    return app.test_client()
```

### Using the Flask Test Client for API routes

This is explained in the Flask documentation
in [Sending Requests with the Test Client](https://flask.palletsprojects.com/en/3.0.x/testing/#sending-requests-with-the-test-client)
which you should read now.

The general structure is:

1. Pass the Flask test client fixture to the test function.
2. Use the test client to make an HTTP request to one of your API routes. Assign the response object to a variable.
3. Access parameter of the response object and use assertions to check the validity.

The response object has various attributes, you will likely use the following:

- the JSON payload (`response.json`)
- the HTTP status code (`request.status_code`)
- page content (`response.data`). This is not relevant for the API routes so is not covered in this tutorial.
- page header details such as the content type (`response.header["Content-Type"]`). The content type for JSON
  is `"application/json"`

The more common [HTTP status codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status) you might expect are:

- 404 NOT FOUND
- 200 OK for successful GET, DELETE, or PATCH requests
- 201 CREATED for POST or PUT requests creating a new resource
- 400 BAD REQUEST e.g. for a badly formatted resource
- 500 INTERNAL SERVER ERROR This might indicate a problem with the request, or might indicate a problem in the server
  side code.

To see what the attributes of the Flask response object look like; add the following code to `test_routes.py` and run
it.:

```python
def test_print_response_params(client):
    """
    This is just so you can see what type of detail you get in a response object.
    Don't use this in your tests!
    """
    response = client.get("/regions")
    print("Printing response.headers:")
    print(response.headers)
    print('\n Printing response.headers["Content-Type"]:')
    print(response.headers['Content-Type'])
    print("Printing response.status_code:")
    print(response.status_code)
    print("Printing response.data:")
    print(response.data)
    print("Printing response.json:")
    print(response.json)
```

Now delete the code you just added as you don't need it in the test code!

### Test the Region GET routes

The following test code tests the 'happy path' of the Region GET routes.

Add the code to `test_routes.py` and run the tests:

```python
def test_get_regions_status_code(client):
    """
    GIVEN a Flask test client
    WHEN a request is made to /regions
    THEN the status code should be 200
    """
    response = client.get("/regions")
    assert response.status_code == 200


def test_get_regions_json(client):
    """
    GIVEN a Flask test client
    AND the database contains data of the regions
    WHEN a request is made to /regions
    THEN the response should contain json
    AND a JSON object for Tonga should be in the json
    """
    response = client.get("/regions")
    assert response.headers["Content-Type"] == "application/json"
    tonga = {'NOC': 'TGA', 'notes': None, 'region': 'Tonga'}
    assert tonga in response.json
```

Now add tests for the variable route which takes a variable for the NOC code:

```python
def test_get_specified_region(client):
    """
    GIVEN a Flask test client
    AND the 5th entry is AND,Andorra,
    WHEN a request is made to /regions/AND
    THEN the response json should match that for Andorra
    AND the response status_code should be 200
    """
    and_json = {'NOC': 'AND', 'notes': None, 'region': 'Andorra'}
    response = client.get("/regions/AND")
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200
    assert response.json == and_json
```

Test for when the region does not exist:

```python
def test_get_region_not_exists(client):
    """
    GIVEN a Flask test client
    WHEN a request is made for a region code that does not exist
    THEN the response status_code should be 404 Not Found
    """
    response = client.get("/regions/AAA")
    assert response.status_code == 404
```

This tests fails when you run it. This is because we have not yet added any error handling to the routes in `routes.py`
so it fails with a SQLAlchemy.exc.NotFound error rather than returning an HTTP error. You will return to this next
week.

If you want to make it work now, then add the following error handler function to `routes.py` _and_ modify the route:

```python
from flask import current_app as app, abort, jsonify
from sqlalchemy.exc import SQLAlchemyError
from paralympics import db
from paralympics.models import Region
from paralympics.schemas import RegionSchema

region_schema = RegionSchema()


@app.errorhandler(404)
def resource_not_found(e):
    """ Error handler for 404.

        Args:
            HTTP 404 error
        Returns:
            JSON response with the validation error message and the 404 status code
        """
    return jsonify(error=str(e)), 404


@app.get('/regions/<code>')
def get_region(code):
    """ Returns one region in JSON.

    Returns 404 if the region code is not found in the database.

    Args:
        code (str): The 3 digit NOC code of the region to be searched for
    Returns: 
        JSON for the region if found otherwise 404
    """
    # Try to find the region, if it is not found, catch the error and return 404
    try:
        region = db.session.execute(db.select(Region).filter_by(NOC=code)).scalar_one()
        result = region_schema.dump(region)
        return result
    except SQLAlchemyError as e:
        # See https://flask.palletsprojects.com/en/2.3.x/errorhandling/#returning-api-errors-as-json
        abort(404, description="Region not found.")
```

### Test the Region POST route

Check that a new Region can be added. To do this you need to pass the JSON to create the route to the test.

```python
def test_post_region(client):
    """
    GIVEN a Flask test client
    AND valid JSON for a new region
    WHEN a POST request is made to /regions
    THEN the response status_code should be 201
    """
    # JSON to create a new region
    region_json = {
        "NOC": "ZZZ",
        "region": "ZedZedZed"
    }
    # pass the JSON in the HTTP POST request
    response = client.post(
        "/regions",
        json=region_json,
        content_type="application/json",
    )
    # 201 is the HTTP status code for a successful POST or PUT request
    assert response.status_code == 201
```

Check that if a request to add a new region fails validation, then it returns a 400 error.

```python
def test_region_post_error(client):
    """
        GIVEN a Flask test client
        AND JSON for a new region that is missing a required field ("region")
        WHEN a POST request is made to /regions
        THEN the response status_code should be 400
        """
    missing_region_json = {"NOC": "ZZY"}
    response = client.post("/regions", json=missing_region_json)
    assert response.status_code == 400
```

This tests fails when you run it. This is because we have not yet added any error handling to the routes in `routes.py`
so it fails with
a Marshmallow schema validation error rather than returning an HTTP error. You will return to this next
week.

If you want to make it work now, then add the following error handler function to `routes.py` and modify the route:

```python
from flask import current_app as app
from marshmallow.exceptions import ValidationError


@app.errorhandler(ValidationError)
def register_validation_error(error):
    """ Error handler for marshmallow schema validation errors.

    Args:
        error (ValidationError): Marshmallow error.
    Returns:
        HTTP response with the validation error message and the 400 status code
    """
    response = error.messages
    return response, 400
```

### Test the Region PATCH route

Add a new pytest fixture to add a new region to the database:

```python
import pytest
from sqlalchemy import exists
from paralympics import db
from paralympics.models import Region


@pytest.fixture(scope='function')
def new_region(app):
    """Create a new region and add to the database.

    Adds a new Region to the database and also returns an instance of that Region object.
    """
    new_region = Region(NOC='NEW', notes=None, region='A new region')
    with app.app_context():
        db.session.add(new_region)
        db.session.commit()

    yield new_region

    # Remove the region from the database at the end of the test if it still exists
    with app.app_context():
        region_exists = db.session.query(exists().where(Region.NOC == 'NEW')).scalar()
        if region_exists:
            db.session.delete(new_region)
            db.session.commit()
```

Add a test for the PATCH route that uses the new fixture:

```python
def test_patch_region(client, new_region):
    """
        GIVEN an existing region
        AND a Flask test client
        WHEN an UPDATE request is made to /regions/<noc-code> with notes json
        THEN the response status code should be 200
        AND the response content should include the message 'Region <NOC_code> updated'
    """
    new_region_notes = {'notes': 'An updated note'}
    code = new_region['NOC']
    response = client.patch(f"/regions/{code}", json=new_region_notes)
    assert response.json['message'] == 'Region NEW updated.'
    assert response.status_code == 200
```

You should add tests for PATCH requests that fail validation; however the tests will fail until appropriate validation
is added to the PATCH route which will be covered in week 5.

### Test the Region DELETE route

This uses the 'new region' fixture you created for the PATCH route test.

```python
def test_delete_region(client, new_region):
    """
    GIVEN an existing region in JSON format
    AND a Flask test client
    WHEN a DELETE request is made to /regions/<noc-code>
    THEN the response status code should be 200
    AND the response content should include the message 'Region {noc_code} deleted.'
    """
    # Get the NOC code from the JSON which is returned in the new_region fixture
    code = new_region['NOC']
    response = client.delete(f"/regions/{code}")
    assert response.status_code == 200
    assert response.json['message'] == 'Region NEW deleted.'

```

## Write tests for the Event routes

Try and write tests similar to the above Region routes for the Event routes.

Tests for errors will fail as the error handling required in the routes has not yet been applied, this will be
covered in the week 5 tutorial.

## Don't forget COMP0035 testing
Also consider setting up a GitHub Actions workflow to run the tests.
