# SAMBAH

The Subsetter And Multi-dimensional Batched Aggregation in Harmony (SAMBAH) chain
executes several services:

1. **CMR Query**: Retrieves information from the Common Metadata Repository (CMR) ([source](https://github.com/nasa/harmony/tree/main/services/query-cmr))
2. **PODAAC L2-Subsetter** (optional): Performs subsetting on level-2 data granules ([source](https://github.com/podaac/l2ss-py))
3. **Batchee**: Groups together filenames so that further operations (such as concatenation) can be performed separately on each group of files ([source](https://github.com/nasa/batchee))
4. **Stitchee**: Concatenates netCDF data along an existing dimension ([source](https://github.com/nasa/stitchee))
5. **PODAAC CONCISE**: Concatenates netCDF data along a newly created dimension ([source](https://github.com/podaac/concise))

## Known Limitations

-

## Missions supported

The SAMBAH service chain is currently configured to work only with data collections
from the Tropospheric Emissions: Monitoring of Pollution (TEMPO) mission.

## References

- Service (UMM-S) record ID in CMR: [S2940253910-LARC_CLOUD](https://cmr.earthdata.nasa.gov/search/services.umm_json?concept_id=S2940253910-LARC_CLOUD)
- Service versions in Harmony Production: <https://harmony.earthdata.nasa.gov/versions>
- Harmony API - Service Capabilities: <https://harmony.earthdata.nasa.gov/docs#service-capabilities>
