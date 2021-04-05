from tinytag import TinyTag

if __name__ == '__main__':

    path = "/Users/joelpridgen/Downloads/065_-_Those_Who_Directed_This_Journey.flac"
    tag = TinyTag.get(path)
    print(type(tag.album))
