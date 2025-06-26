# SEPARATE
<p align="center">
  <img src="../images/header.png" alt="SEPARATE Banner" width="600"/>
</p>

## Example Datasets

To help users get started quickly, we include two example datasets:
| Filename                             | Description                                                                 |
|--------------------------------------|-----------------------------------------------------------------------------|
| `FixedInterval_TBRG_Example.xlsx`    | Example dataset logged at regular intervals using fixed time steps.      |
| `CumulativeTips_TBRG_Example.xlsx`   | Example dataset with cumulative tip logging style (e.g., HOBO loggers).  |

Each file contains two columns:
1. **Timestamp** in the format `MM/DD/YY HH:MM:SS`
2. **Rainfall Value** — either:
   - Cumulative tip count (`Cumulative Tips` format), or
   - Rainfall per interval (`Fixed Interval` format)

Both files are preformatted to match SEPARATE’s input requirements. You can use them to test the interface, explore SEPARATE’s options, or verify that your installation is working correctly.

The [`Outputs`](./Outputs) folder contains the results from running both datasets with a 15-minute storm intensity threshold for plotting.

<div align="center">
  <img src="../images/fixed_example.png" alt="Fixed Interval Input Example" width="500"/>
  <br>
  <em>Figure: Fixed interval usage example.</em>
</div>

<br>

<div align="center">
  <img src="../images/tips_example.png" alt="Cumulative Tips Input Example" width="500"/>
  <br>
  <em>Figure: Cumulative tips usage example.</em>
</div>





