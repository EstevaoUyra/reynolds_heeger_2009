# Qualitative Sanity Checks

These scripts are exploratory diagnostics for Phase B implementation work.
They are not pass/fail tests. Run them when narrow data-claim failures do not
make the model behavior easy to see.

Each script writes PNGs and text summaries to a sibling `*_outputs/` directory,
which is ignored by git.

```bash
.venv/bin/python -m pip install -e ".[sanity]"
.venv/bin/python models/reynolds_heeger_2009/implementation/sanity_checks/check_stimulus_drive.py
.venv/bin/python models/reynolds_heeger_2009/implementation/sanity_checks/check_pipeline_trace.py
.venv/bin/python models/reynolds_heeger_2009/implementation/sanity_checks/check_contrast_sweeps.py
```
