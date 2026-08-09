## What the CRAN package `sharp` is (R)

CRAN’s `sharp` package (“Stability-enHanced Approaches using Resampling Procedures”) implements methods for **stability selection** and **consensus clustering**. It uses **resampling** to improve reliability by **calibrating hyperparameters** to maximize a model-stability measure under a **null hypothesis** where all selection (or co-membership) probabilities are identical. <citation src="2"></citation>

It provides ready implementations for (among others):
- **Stability selection** using **LASSO regression** (via `glmnet`), **sparse PCA**, **sparse/group PLS**, and **graphical LASSO**.
- **Consensus clustering** using methods such as **hierarchical clustering**, **partitioning around medoids (PAM)**, **K-means**, and **Gaussian mixture models**. <citation src="2"></citation>

## Install it from CRAN

```r
install.packages("sharp")
```
<citation src="1,2"></citation>

(That CRAN page also lists version info such as current package version and dependencies.) <citation src="2"></citation>

## Minimal usage examples (from the package overview)

### 1) Stability selection for regression (LASSO)
```r
library(sharp)

stab_reg <- VariableSelection(xdata = x_reg, ydata = y_reg)
SelectedVariables(stab_reg)
```
<citation src="1"></citation>

### 2) Graphical model stability selection (graphical LASSO)
```r
stab_ggm <- GraphicalModel(xdata = x_ggm)
Adjacency(stab_ggm)
```
<citation src="1"></citation>

### 3) Consensus clustering
```r
stab_clust <- Clustering(xdata = x_clust)
Clusters(stab_clust)
```
<citation src="1"></citation>

## Hyperparameter calibration check (recommended)

The package strongly recommends checking calibration using:
- `CalibrationPlot()` on the output from the main functions.
It also supports `print()`, `summary()`, and `plot()` on those outputs. <citation src="1"></citation>
