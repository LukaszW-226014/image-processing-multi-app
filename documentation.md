
<h1 align="center">ALGORYTM DETEKCJI NOWOTWORU SKÓRY</h1>
<h3 align="center">Etap 1 - wykrywanie krawędzi zmiany</h3>
<br>
<p>Serwis dostępny na: [melanoma.tk](http://melanoma.tk)</p>
<br>    

<p>Importy bibliotek:</p>
```python
import os
import glob
import random
import numpy as np
import cv2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
```

<p>Ustawienie ścieżek dostępu:</p>
```python
imagePath = os.getcwd() + '/uploads/'
histogramPath = os.getcwd() + '/static/histograms/'
filename = "melanomaCancer.jpg"
```

<h2 align="center">Krok 0: Pobranie od użytkownika obrazu</h2>
<br>
<p align="justify">Użytkownik "uploaduje" obraz swojej zmiany skóry:</p> 
<br>
<center><img src="/Users/japko/Development/Python/image-processing-multi-app
/static/melanomaCancer.jpg" width=50%></center>
<br>

<p align="justify">Celem algorytmu jest to aby po przetworzeniu obrazu zwrócił prawdopodobieństwo, z jakim ta zmiana jest nowotworem.</p>
<br>


```python
# Step 1 read convert to grayscale image
img = cv2.imread(imagePath + filename, cv2.IMREAD_GRAYSCALE)
# save result
save = cv2.imwrite(histogramPath + "0Started.jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
```





<h2 align="center">Krok 1: Wczytanie obrazu i konwersja do skali szarości</h2>
<br>
<center><img src="static/histograms/0Started.jpg" width=50%></center>
<br>
<p align="justify">Obraz jest wczytywany przy pomocy metody imread() z biblioteki opencv (cv2) z parametrem IMREAD_GRAYSCALE co oznacza konwersję wczytanego kolorowego obrazu do obrazu w skali szarości.</p>
<br>


```python
# Step 2: Gaussian filter
denoised = cv2.GaussianBlur(img, (5, 5), 0)
# save result
cv2.imwrite(histogramPath + "1denoised.jpg", denoised, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
```



<h2 align="center">Krok 2: Filtr Gaussa</h2>
<br>
<center><img src="static/histograms/1denoised.jpg" width=50%></center>
<br>
<p align="justify">Obraz jest wygładzany przy pomocy dolnoprzepustowego filtru Gaussa.</p>
<br>


```python
#Step 3: Thresholding
ret, thresh2 = cv2.threshold(denoised, 127, 255, cv2.THRESH_BINARY_INV)
# save result
save = cv2.imwrite(histogramPath + "2Tresh.jpg", thresh2, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
```



<h2 align="center">Krok 3: Thresholding - binaryzacja</h2>
<br>
<center><img src="static/histograms/2Tresh.jpg" width=50%></center>
<br>
<p align="justify">Obraz jest poddawany binaryzacji z progiem 127 powyżej, którego pixelom przypisywana jest wartość 0, a poniżej wartość 1.</p>
<br>


```python
denoisedTresh = cv2.GaussianBlur(thresh2, (5, 5), 0)
# save result
save = cv2.imwrite(histogramPath + "3denoisedThresh.jpg", denoisedTresh, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
```





<h2 align="center">Krok 4: Filtr Gaussa</h2>
<br>
<center><img src="static/histograms/3denoisedThresh.jpg" width=50%></center>
<br>
<p align="justify">Zbinaryzowany obraz jest poddawany kolejnej filtracji Gaussa w celu wygładzenia krawędzi "dziór", które będą w następnym kroku wypełniane.</p>
<br>


```python
flood_fill = denoisedTresh.copy()
```


```python
h, w = denoisedTresh.shape[:2]
mask = np.zeros((h + 2, w + 2), np.uint8)

# Step 5: Floodfill from point (0, 0)
fl = cv2.floodFill(flood_fill, mask, (0, 0), 255)
```






```python
# Invert floodfilled image
flood_fill_inv = cv2.bitwise_not(flood_fill)
# save result
save = cv2.imwrite(histogramPath + "5invOut.jpg", flood_fill_inv, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
```




<h2 align="center">Krok 5: Wytworzenie maski</h2>
<br>
<center><img src="static/histograms/5invOut.jpg" width=50%></center>
<br>
<p align="justify">Wytworzenie maski czarnych dziór wewnątrz obiektu zmiany, która w następnej operacji logicznej wypełni cały obszar zmiany.</p>
<br>


```python
# Combine the two images to get the foreground.
filled_out = denoisedTresh | flood_fill_inv
# save result
save = cv2.imwrite(histogramPath + "6Out.jpg", filled_out, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
```



<h2 align="center">Krok 6: Wypełnienie obszaru zmiany</h2>
<br>
<center><img src="static/histograms/6Out.jpg" width=50%></center>
<br>
<p align="justify">Obraz po operacji OR na masce i obrazie z kroku 4 jest już zmianą która w całości jest wypełniona, dzoęki czemu możemy teraz łatwo wykryć krawędzie.</p>
<br>


```python
# Step 6: Detect edges - Laplacian
filter2 = cv2.Laplacian(filled_out, cv2.CV_64F)
# save result
save = cv2.imwrite(histogramPath + "7detectedEdges.jpg", filter2, [int(cv2.IMWRITE_JPEG_QUALITY), 95]) 
```








<h2 align="center">Krok 7: Laplacjan</h2>
<br>
<center><img src="static/histograms/7detectedEdges.jpg" width=50%></center>
<br>
<p align="justify">Wykonanie wyostrzania Laplacjanu pozwoliło na eleganckie wyznaczenie krawędzi zmiany skórnej, co jest bardzo ważne do dalszych kroków wyliczania prawdopodobieństwa nowotworowości zmiany opartych na symetri i regularności zmiany skórnej.</p>
<br>


