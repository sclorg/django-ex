# Overview

This is a beta prototype for the eDivorce project, an app that assists the user
in preparing the legal filings for joint, uncontested divorce.

## Current architecture

As this is a heavily UX driven effort, the implementation is extremely simple
and orthodox, to make it easy for interface changes to be iterated through.

All pages outlined in the page flow document have corresponding templates where
the form elements will be built out (Django Forms won't be used; this keeps all
the form/interaction logic in the template).  

The underlying models are likewise very shallow: a profile model holding user
specific indo; a question model for mapping questions from the UX master
document to a user's responses; a legal form model for each of the forms to be
generated and a through model for mapping questions into the form and having a
transformation step on user values.  (Note that the field mapping drawn from the
PDFs is not represented internally here; that effort is solely to cross-map
re-used fields on the forms).
