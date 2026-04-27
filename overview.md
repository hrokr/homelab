This technical baseline defines a localized media-platform-as-code. It prioritizes data portability, offline resilience, and high information density.

Overview: A homelab server using a Beelink connected via USB to two 8TB HDDs, `Primary` and `Failover`. A third 8TB HDD, `Offsite` is current source of most material. Once all data is moved, it will be used for a third (and offsite) storage.

The Beelink runs, via docker, containers for the following current and future purposes.

 * Movie server
 * Music server
 * Document server (pending)
 * Document enrichment (via PaperPusher, under delayed development)


## Hardware Architecture

### Computing Node: Beelink Mini PC
* **Processor:** Beelink handles 24/7 production services.

### Storage Array: 3x 8TB HDDs (USB Connectivity)
* **Configuration:** * **Primary:** 8TB HDD mounted to `/mnt/primary` using Btrfs subvolume `@data`.
    * **Failover:** 8TB HDD mounted to `/mnt/failover` using Btrfs subvolume `data_reconcile_v1`.
    * **Cold Storage:** 8TB HDD (Pending integration).
* **Justification:** Btrfs is chosen over ZFS for its flexibility in adding mismatched drives and its native subvolume/snapshot capabilities, which are easier to manage in a non-ECC USB environment.

---

## Software Stack & Automation

### Orchestration: Docker & Docker Compose
* **Services:** Jellyfin (Media Server), TinyMediaManager (Metadata Management), Navidrome (Audio), Traefik (Edge Router), Prefect/Airflow (Orchestration).
* **Justification:** Containers isolate dependencies for local LLM experiments and the media stack. Traefik provides dynamic discovery, allowing service additions without manual proxy reloads.

### Routing: Traefik & Avahi (mDNS)
* **Mechanism:** Traefik labels handle container routing; Avahi broadcasts `.local` TLDs.
* **Alternative:** Tailscale is utilized for remote peer-to-peer access, but Avahi is the primary for standalone offline resolution.

### Metadata Strategy: Sidecar NFO/JPG
* **Workflow:** TinyMediaManager (TMM) scrapes and writes assets directly to movie directories.
* **Justification:** Avoids lock-in to Jellyfin’s internal database. Metadata becomes a physical asset that survives drive migration or library resets.

### Custom Tooling: PaperPusher & Sync Scripts
* **PaperPusher:** Python-based document scanning pipeline utilizing Airflow and SQLite.
* **Synchronization:** Shell scripts utilizing `rsync` for primary-to-failover mirroring.
    ```bash
    rsync -av --delete /mnt/primary/ /mnt/failover/
    ```

---

## Configuration Files

### /etc/fstab (Persistence)
Uses UUIDs to prevent device name swapping common in USB-based storage.
```text
UUID=75face37-9c8b-47f0-b655-e0cbe8cbc9b3 /mnt/primary btrfs defaults,subvol=@data 0 2
UUID=d5f98c4a-66fa-41c2-a251-31b3eac49283 /mnt/failover btrfs defaults,subvol=data_reconcile_v1 0 2
```

### docker-compose.yml (Core Logic)
Standardizes service ports and Traefik rules.
```yaml
services:
  traefik:
    image: traefik:v2.10
    volumes: [/var/run/docker.sock:/var/run/docker.sock]
  jellyfin:
    image: jellyfin/jellyfin
    labels:
      - traefik.http.routers.jellyfin.rule=Host(jellyfin.local)
    volumes:
      - /mnt/primary/@data/Videos:/media/movies
```

### Prompt for missing data
To complete the technical profile, I require:
1.  The specific version or model of the Beelink for TDP and transcoding context.
2.  The current directory structure of the PaperPusher repository for the automation section.
3.  Any specific Python scripts used for the HDDs failover logic beyond standard `rsync` calls.

Do you have the current `traefik.yml` or `static_config` to include, or should I assume default provider-based discovery?


The tree for the project is:
tree -L 2
.
├── backups
│   ├── beets_checkpoint_2026-02-09_1807.tar.gz
│   └── beets_metadata_2026-02-09.tar.gz
├── config
│   ├── beets
│   ├── jellyfin
│   ├── minio
│   ├── navidrome
│   ├── picard
│   ├── postgres
│   ├── prefect
│   ├── tmm
│   ├── tmm_config
│   └── traefik
├── docker-compose.yaml
├── docs
├── jellyfin
│   └── config
├── mount
├── music
├── navidrome
│   ├── cache
│   └── navidrome.db
├── postgres-data  [error opening dir]
├── scripts
│   ├── ingest_quality_logs
│   ├── ingest_quality.py
│   ├── merge_music.py
│   ├── move_remaining.py
│   ├── quality_sync.py
│   ├── sync-backups.sh
│   └── sync_btrfs.py
├── sudo
└── sync-backups.sh



