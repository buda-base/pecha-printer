# པར་གཞི་སྒྲིག་ཆས། Pecha Printer
Program to convert a pdf into a ready to print "Pecha", traditional Tibetan volumes.

### ཕབ་ལེན། Download Installer

* [སྒེའུ་ཁུང་རྟགས་ཅན། Windows](https://github.com/buda-base/pecha-printer/releases/download/v1.3/PechaPrinter_1.3.exe)

## ཚད་མཐོའི་འཇུག་སྤྲོད། Advanced Install
* ཀུ་ཤུ་རྟགས་ཅན་ཆེད། Mac & Linux:
    1. [ཕེ་ཐོན་མ་ལག་ཐོན་རིམ་ 3.7 ཕབ་ལེན་བྱས་ཏེ་འཇུག་སྤྲོད་བྱོས། Install Python 3.7](https://www.saintlad.com/install-python-3-on-mac/)
    2. [པར་གཞི་སྒྲིག་ཆས་ཀྱི་ཁུག་མ་ཕབ་ལེན་བྱོས། Download Pecha Printer](https://github.com/buda-base/pecha-printer/archive/master.zip)
    3. Open Terminal and run `python3 install.py`
    4. Open Terminal and run `python3 pechaprinter.pyw`

## Why use pecha-printer?
- printing one pecha page per paper sheet wastes a lot of paper
- grouping images 3 by 3 in photoshop is difficult and time consuming
![pecha-printer logic (15)](https://user-images.githubusercontent.com/17675331/133715523-f748843a-ec64-43dd-aa32-32c708719d9f.png)
- A requires a lot of reordering of pecha pages,
- B only requires to combine the 3 piles in order to get a pecha ready for reading!
![pecha-printer logic (12)](https://user-images.githubusercontent.com/17675331/133715222-d1248ecc-80b2-4129-8051-cc67e5a3afae.png)
![pecha-printer logic (13)](https://user-images.githubusercontent.com/17675331/133715228-44eb665a-eab5-42fb-bc34-bc26bc97eec7.png)


## Development Roadmap
### To do:
- [x] Windows installer
- [ ] Mac installer
- [x] redesign the UI
- [x] localization
- [ ] custom paper size
- [ ] option to binarise all images for unity
- [ ] combine multiple pdfs
- [x] bundle for distribution

### Wish list:
- split pdfs on outline and name files after section names

## License

The code is Copyright 2019 Buddhist Digital Resource Center, and is provided under [Apache License 2.0](LICENSE).
