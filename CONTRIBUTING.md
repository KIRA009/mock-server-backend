When contributing to this repository, please first discuss the change you wish to make via issue, email, or any other method with the owners of this repository before making a change. 
# Pull Request Process
- Before starting to work on a new feature, make sure to go through existing issues to see if the feature request has already been addressed.
- Raise an issue giving an overview of the feature and your plan of action on how to address it.
- Create a feature branch from where you want to base your branch (usually the master branch).
- Ensure that commits are atomic and logical, and that each commit deals with a small yet significant part of the feature, so that reverting changes are easy and manageable.
- Check for unnecessary whitespace with git diff --check before 
committing.
- Make sure your commit messages are of the following template
    ```
    [feat|fix|refactor] {msg}

    Added following
    -

    Changed following
    -

    Fixed following
    -
    ```
- Write tests for any new user facing feature.
- Ensure that the pr does not fail any existing tests.

# Contributors
- [Shohan](https://github.com/KIRA009/)