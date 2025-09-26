import sys

def main():
    try:
        import tools.content_analysis_tools as cat
        import tools.image_sourcing_tools as ist

        print("content_tools:", [getattr(f, '__name__', str(f)) for f in cat.get_content_analysis_tools()])
        # image_sourcing_tools provides get_image_sourcing_tools()
        print("image_tools:", [getattr(f, '__name__', str(f)) for f in ist.get_image_sourcing_tools()])
    except Exception as e:
        print("IMPORT_ERROR", e)
        raise


if __name__ == '__main__':
    main()
