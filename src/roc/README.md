# Understanding AUC - ROC Curve
In Machine Learning, performance measurement is an essential task. So when it comes to a classification problem, we can count on an AUC - ROC Curve. When we need to check or visualize the performance, we use the AUC *(Area Under The Curve)* ROC *(Receiver Operating Characteristics)* curve. It is one of the most important evaluation metrics for checking any classification model’s performance. It is also written as AUROC (Area Under the Receiver Operating Characteristics)

Here, we aim to answer the following questions:

1. What is the AUC - ROC Curve?
2. Defining terms used in AUC and ROC Curve.
3. How to speculate the performance of the model?
4. Relation between Sensitivity, Specificity, FPR, and Threshold.
5. How to use AUC - ROC curve for the multiclass model? *(OPTIONAL READING)* 

## 👉 Part 1: What is the AUC - ROC Curve?
AUC - ROC curve is a performance measurement for the classification problems at various threshold settings. ROC is a probability curve and AUC represents the degree or measure of separability. It tells how much the model is capable of distinguishing between classes. Higher the AUC, the better the model is at predicting 0 classes as 0 and 1 classes as 1. By analogy, the Higher the AUC, the better the model is at distinguishing between tweets with hate/offensive text or not.

The ROC curve is plotted with **True Positive Rate (TPR)** against the **False Positive Rate (FPR)** where TPR is on the y-axis and FPR is on the x-axis as shown in the figure below.
<p align="center">
   <img src="../../images/roc-part1.png" alt="[YOUR_ALT]"/>
</p>

## 👉 Part 2: Defining terms used in AUC and ROC Curve.

- **TPR (True Positive Rate) / Recall /Sensitivity** = True Positive (TP) / True Positive (TP) + False Negative (FN)
- **Specificity** = True Negative (TN) / True Negative (TN) + False Positive (FP)
- **FPR (False Negative Rate)** = 1 - **Specificity** = False Positive (FP) / True Negative (TN) + False Positive (FP)

## 👉 Part 3: How to speculate about the performance of the model?
An excellent model has AUC near to the 1 which means it has a good measure of separability. A poor model has an AUC near 0 which means it has the worst measure of separability. In fact, it means it is reciprocating the result. It is predicting 0s as 1s and 1s as 0s. And when AUC is 0.5, it means the model has no class separation capacity whatsoever.

Let’s interpret the above statements.

As we know, ROC is a curve of probability. So let's plot the distributions of those probabilities:
Note: Red distribution curve is of the positive class (tweets classified as hate/offensive) and the green distribution curve is of the negative class (tweets not classified as hate/offensive).

<p align="center">
   <img src="../../images/roc-part2.png" alt="[YOUR_ALT]"/>
</p>

This is an ideal situation. When two curves don’t overlap at all means model has an ideal measure of separability. It is perfectly able to distinguish between positive class and negative class.

<p align="center">
   <img src="../../images/roc-part3.png" alt="[YOUR_ALT]"/>
</p>
When two distributions overlap, we introduce type 1 and type 2 errors. Depending upon the threshold, we can minimize or maximize them. When AUC is 0.7, it means there is a 70% chance that the model will be able to distinguish between positive class and negative class.

<p align="center">
   <img src="../../images/roc-part4.png" alt="[YOUR_ALT]"/>
</p>
This is the worst situation. When AUC is approximately 0.5, the model has no discrimination capacity to distinguish between positive class and negative class.

<p align="center">
   <img src="../../images/roc-part5.png" alt="[YOUR_ALT]"/>
</p>
When AUC is approximately 0, the model is actually reciprocating the classes. It means the model is predicting a negative class as a positive class and vice versa.


## 👉 Part 4: The relation between Sensitivity, Specificity, FPR, and Threshold.
Sensitivity and Specificity are inversely proportional to each other. So when we increase **Sensitivity**, **Specificity** decreases, and vice versa.

When we decrease the **threshold**, we get more positive values thus it increases the sensitivity and decreasing the specificity.

Similarly, when we increase the threshold, we get more negative values thus we get higher specificity and lower sensitivity.

As we know FPR is 1 - specificity. So when we increase TPR, FPR also increases and vice versa.

## 👉 Part 5: How to use the AUC ROC curve for the multi-class model?
In a multi-class model, we can plot the N number of AUC ROC Curves for N number classes using the One vs ALL methodology. So for example, If you have **three** classes named X, Y, and Z, you will have one ROC for X classified against Y and Z, another ROC for Y classified against X and Z, and the third one of Z classified against Y and X.

## Recommended Reading on AUC-ROC.  
- YouTube video by StatQuest with Josh Starmer [here](https://www.youtube.com/watch?v=4jRBRDbJemM)  
- Clearly explained blog by Analytics Vidhya [here](https://www.analyticsvidhya.com/blog/2020/06/auc-roc-curve-machine-learning/)

Thanks for Reading! 👏👏

