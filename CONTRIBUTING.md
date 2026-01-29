# Contributing to Smart-Proxy-Server

First off, thank you for considering contributing to Smart-Proxy-Server! It's people like you that make this project great.

## Where do I go from here?

If you've noticed a bug or have a feature request, [make one](https://github.com/hasanmehediii/CSE-3111-Project/issues/new)! It's generally best if you get confirmation of your bug or approval for your feature request this way before starting to code.

### Fork & create a branch

If this is something you think you can fix, then [fork the repository](https://github.com/hasanmehediii/CSE-3111-Project/fork) and create a branch with a descriptive name.

A good branch name would be (where issue #38 is the ticket you're working on):

```sh
git checkout -b 38-add-awesome-new-feature
```

### Get the project running

To get the project running, you'll need to have Python 3 installed. Then, you can create a virtual environment and install the dependencies:

```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

To run the proxy server:

```sh
python app.py
```

### Make your changes

Make your changes to the code, and make sure to add tests for your changes.

### Commit your changes

Commit your changes with a descriptive commit message.

```sh
git commit -m "feat: Add awesome new feature"
```

### Push your changes

Push your changes to your fork.

```sh
git push origin 38-add-awesome-new-feature
```

### Open a pull request

Open a pull request to the `main` branch.

### Wait for a review

Once you've opened a pull request, a maintainer will review your changes. We may ask you to make changes to your code. If your changes are approved, we'll merge them into the `main` branch.

And that's it! Thank you for your contribution!
