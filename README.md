# SOC AI Platform

## Run Daemon
```bash
cd daemon
python soc_pipeline_daemon.py

cd ui
python app.py

mysql soc_ai < sql/schema.sql
