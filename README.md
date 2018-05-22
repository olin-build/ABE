# ABE

[![Build Status](https://travis-ci.org/olin-build/ABE.svg?branch=dev)](https://travis-ci.org/olin-build/ABE)
[![Coverage](https://codecov.io/gh/olin-build/ABE/branch/dev/graph/badge.svg)](https://codecov.io/gh/olin-build/ABE)

**ABE** (Amorphous Blob of Events) is Olin's student-built store of information
about Olin events. It enables the creation of digital experiences that share
information about past, present, and upcoming events.

## Using

### As a Calendar User

You want ABE's web calendar front end, [abe-web][abe-web].

## As a Developer

The ABE API lets an application read and modify events, labels, and calendar
subscriptions. Read about ABE's API documentation
[here](https://github.com/olin-build/ABE/wiki/ABE-API).

ABE can also be used to verify that a user is inside the Olin intranet, and/or
is a member of the Olin community (as demonstrated by possession of an
`olin.edu` email address). See the documentation on [Sign in with
ABE](https://github.com/olin-build/ABE/wiki/Sign-in-with-ABE).

## Contributing

Please check out the [the open issues][issues]. Good first issues are labeled with ["good first issue"][good-first-issue]. Also see the [Contribution Guide][contributing].

## Built With ABE

ABE is a platform. Some online experiences that use the data in ABE include:

* [Olin Events][abe-web] is a web view of the Olin calendar. It can also be used
  to subscribe other calendar programs, such as Google Calendar and desktop and
  mobile calendar clients, to ABE; and to connect ABE to other calendars.
* [FUTUREboard](https://github.com/olinlibrary/futureboard)  is a digital
  signage platform for sharing of media, supplemented by information about
  events happening on campus.
* [ABE Event Schedule](https://github.com/osteele/abe-event-schedule) is an
  experiment in deriving a conference-track-style schedule from ABE events.

[abe-web]: https://github.com/olin-build/abe-web
[contributing]: ./docs/CONTRIBUTING.md
[good-first-issue]: https://github.com/olin-build/ABE/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22
[issues]: https://github.com/olin-build/ABE/issues
