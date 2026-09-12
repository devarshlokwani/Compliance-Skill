# demo-django (fixture)

Cross-stack regression test. The other fixtures are JavaScript; this one exists
to prove the scanner is not quietly Next.js-only.

It checks that:

- project shape is detected from `manage.py` and `requirements.txt`, not from
  `package.json`
- personal data is found in Django ORM field declarations
  (`models.EmailField`, `models.DateField`) rather than Prisma schemas
- launch-readiness checks work against server-rendered Jinja/Django templates
  rather than a Next.js `metadata` export
- accessibility checks work on plain HTML rather than JSX

Not a real project. `SECRET_KEY` is read from the environment here on purpose —
a real `django-insecure-...` literal would be caught by the secret scanner, and
this fixture needs to exit 0.
