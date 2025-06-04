# SEPARATE

## Example Datasets

To help users get started quickly, we include two example datasets in the [`Example_Datasets`](Example_Datasets/) folder:

| Filename                             | Description                                                                 |
|--------------------------------------|-----------------------------------------------------------------------------|
| `FixedInterval_TBRG_Example.xlsx`    | Example dataset logged at regular intervals using fixed time steps.      |
| `CumulativeTips_TBRG_Example.xlsx`   | Example dataset with cumulative tip logging style (e.g., HOBO loggers).  |

Each file contains two columns:
1. **Timestamp** in the format `MM/DD/YY HH:MM:SS`
2. **Rainfall Value** — either:
   - Cumulative tip count (`Cumulative Tips` format), or
   - Rainfall per interval (`Fixed Interval` format)

Both are preformatted to match SEPARATE’s input requirements. You can use these files to test the interface, explore SEPARATE’s options, or verify that your installation is working correctly.
In the ouputs folder, you can find the results from each of these runs below, using a 15-min. storm intensity for plotting. 

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




