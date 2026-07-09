# Plugin Abstraction Baseline

This contains all of the common logic within plugins to where they can be used across plugins without the need for additional manipulation.

## The General Idea

The setup for this follows Domain-Driven Design to try to ease understanding on the general process within plugins for all maintainers, regardless of experience with the codebase.

The Application layer houses everything that a user notices: Deck Formats, Deck List parsing, and Game Plugin interaction.

The Domain layer houses everything based on how the user would abstract it: A Deck is a group of Cards that have Images.

The Infrastructure layer houses how the plugin interacts with other areas outside of the software: File I/O, Web Requests, and Asset Manipulation.

The intention is that most of the logic for plugins are present within this abstraction. When additional information or logic is required, use the abstraction class as the super class when defining it for a plugin. The main areas that should require this would fall under ``application`` or ``infrastructure``, since special rules could be in place on a game-by-game or format-by-format basis.