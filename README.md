# Flyff Universe EXP Tracker
This is a wonky little tool I created as a workaround until the suggestion to implement an EXP tracker in-game is completed. I have talked to the GMs and they confirmed this is fine to use as it does not automate anything.

I am however not allowed to promote it on the FlyffU discord so good job that  you found this.

![](https://i.imgur.com/ZoWxOG7.png)

# Installing
The tool uses pytesseract for OCR and I cant be fucked to deploy the required  dll along with the tool. Instead, you can do the following:
1. Install python
2. Download the repository
3. Run `python -m pip install -r requirements.txt`
4. Download the [pytesseract executable](https://tesseract-ocr.github.io/tessdoc/Installation.html). Copy the path you dropped the file to and override this line with your path (keep the r at the start).
```py
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

# Usage
1. Set interface scaling to max.

2. Adjust the width of the character window to its minimum like this

![](https://i.imgur.com/rHJsgJ5.png)

3. Align the character window to the top left corner of the screen

4. Take a screenshot of the character window **including the taskbar of your browser** and open it in a photo editing software like PhotoShop. You will need the following pixel values: ![](https://i.imgur.com/rIyoCRK.png)

Once you have them, override them here within the code
```py
EXP_X = 159
EXP_Y = 195
EXP_WIDTH = 90
EXP_HEIGHT = 19
```

5. Start the tool using `python ./exp_tracker.py`. If the tool is in the wrong position, you can override the `TOOL_X` and `TOOL_Y` variables to match the top left corner of the desired screen position.