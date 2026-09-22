flowchart LR
    %% Data Sources
    subgraph SRC["External Input Data"]
        AirNow["AirNow Data<br/>(HourlyData_*.dat)"]
        RAP["RAP Observations<br/>(*.prepbufr.tm00)"]
        GFS_IC["GFS Initial Files<br/>(gfs.*.f006)"]
        GFS_LBC["GFS Boundary Files<br/>(gfs.*.f006-f030)"]
        CHEM_DATA["Emissions Data<br/>(RAVE / GRA2PES)"]
    end

    %% Ingestion & Base Prep
    subgraph PREP["Data Ingestion & Extraction"]
        ioda_airnow["ioda_airnow"]
        ioda_bufr["ioda_bufr"]
        ungrib_ic["ungrib_ic"]
        ungrib_lbc["ungrib_lbc_g01"]
        ic["ic"]
        lbc_g01["lbc_g01"]
        prep_lbc["prep_lbc"]
        prep_chem["prep_chem"]
    end

    %% Initialization Branching: Cold vs Warm Start
    subgraph SETUP["State Setup & Data Assimilation"]
        
        subgraph COLD["COLD START (Cycle 00)"]
            prep_ic_cold["prep_ic<br/>(Coldstart)"]
        end

        subgraph WARM["WARM START (Cycles 01-23)"]
            prev_f01[("Previous Cycle<br/>fcst_f001.done")]
            prep_ic_warm["prep_ic<br/>(Warmstart)"]
            jedivar["jedivar<br/>(JEDI Data Assimilation)"]
        end

    end

    %% Execution & Output
    subgraph RUN["Forecast Execution & Output"]
        fcst["fcst / fcst_l"]
        save_f01["save_for_next_f01"]
        mpassit["mpassit_g00"]
        upp["upp_g00"]
        out_grib[("Final GRIB2 Products")]
    end

    %% Ingestion Connections
    AirNow --> ioda_airnow
    RAP --> ioda_bufr
    GFS_IC --> ungrib_ic --> ic
    GFS_LBC --> ungrib_lbc --> lbc_g01 --> prep_lbc

    %% Coldstart Path (Cycle 00)
    ic -- "Raw MPAS IC" --> prep_ic_cold
    prep_ic_cold -- "Direct Cold Start IC" --> fcst

    %% Warmstart Path (Cycles 01-23)
    prev_f01 -- "1-hr Forecast Restart State" --> prep_ic_warm
    prep_ic_warm -- "Background State" --> jedivar
    ioda_bufr -- "IODA Obs Data" --> jedivar
    jedivar -- "Assimilated Analysis State" --> fcst

    %% Shared Prep Dependencies
    prep_ic_cold --> prep_chem
    prep_ic_warm --> prep_chem
    prep_chem -- "Smoke/Dust Tracers" --> fcst
    prep_lbc -- "Boundary Conditions" --> fcst

    %% Post-Processing Connections
    fcst -- "mpasout.nc (f01)" --> save_f01
    save_f01 -.- "Feeds Next Cycle" .-> prev_f01
    fcst -- "history.nc / diag.nc" --> mpassit --> upp --> out_grib
