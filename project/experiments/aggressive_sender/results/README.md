# Insights

## Large initial window size vs Same window sizes

Attacker will use a much larger initial window size compared to all other normal users.

| Attacker | Attacker with Large initial window size          | All same initial window size                      |
| :------: | ------------------------------------------------ | ------------------------------------------------- |
| control  | ![](exp5/result_500-100-10-10-NoMix-16K-1M.png)  | ![](exp5/result_500-100-10-10-NoMix-16K-16K.png)  |
|    2x    | ![](exp5/result_500-100-10-20-NoMix-16K-1M.png)  | ![](exp5/result_500-100-10-20-NoMix-16K-16K.png)  |
|   80x    | ![](exp5/result_500-100-10-800-NoMix-16K-1M.png) | ![](exp5/result_500-100-10-800-NoMix-16K-16K.png) |

CDF

| Attacker | Attacker with Large initial window size              | All same initial window size                          |
| :------: | ---------------------------------------------------- | ----------------------------------------------------- |
| control  | ![](exp5/result_500-100-10-10-NoMix-16K-1M_CDF.png)  | ![](exp5/result_500-100-10-10-NoMix-16K-16K_CDF.png)  |
|    2x    | ![](exp5/result_500-100-10-20-NoMix-16K-1M_CDF.png)  | ![](exp5/result_500-100-10-20-NoMix-16K-16K_CDF.png)  |
|   80x    | ![](exp5/result_500-100-10-800-NoMix-16K-1M_CDF.png) | ![](exp5/result_500-100-10-800-NoMix-16K-16K_CDF.png) |

## Mixing Protocol vs Unified Protocol

Attacker will use TCP Reno while all other user use TCP Cubic, and attacker will use TCP Cubic while all other user use TCP Reno.

| Attacker | Mix                                             | No Mix                                            |
| :------: | ----------------------------------------------- | ------------------------------------------------- |
| control  | ![](exp5/result_500-100-10-10-Mix-16K-16K.png)  | ![](exp5/result_500-100-10-10-NoMix-16K-16K.png)  |
|    2x    | ![](exp5/result_500-100-10-20-Mix-16K-16K.png)  | ![](exp5/result_500-100-10-20-NoMix-16K-16K.png)  |
|   80x    | ![](exp5/result_500-100-10-800-Mix-16K-16K.png) | ![](exp5/result_500-100-10-800-NoMix-16K-16K.png) |

CDF

| Attacker | Mix                                                 | No Mix                                                |
| :------: | --------------------------------------------------- | ----------------------------------------------------- |
| control  | ![](exp5/result_500-100-10-10-Mix-16K-16K_CDF.png)  | ![](exp5/result_500-100-10-10-NoMix-16K-16K_CDF.png)  |
|    2x    | ![](exp5/result_500-100-10-20-Mix-16K-16K_CDF.png)  | ![](exp5/result_500-100-10-20-NoMix-16K-16K_CDF.png)  |
|   80x    | ![](exp5/result_500-100-10-800-Mix-16K-16K_CDF.png) | ![](exp5/result_500-100-10-800-NoMix-16K-16K_CDF.png) |
