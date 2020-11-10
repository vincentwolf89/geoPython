import os 

inDirectory = 'D:/Projecten/WSRL/safe/lekdata/rasters/'
outDirectory = 'D:/Projecten/WSRL/safe/lekdata/temp/'
  
# Function to rename multiple files 
def main(inDirectory,outDirectory): 
  
    for count, filename in enumerate(os.listdir(inDirectory)): 
        
        dstName = "raster"+str(count)+".ascii"
        src =inDirectory + filename 
        dst =outDirectory + dstName 
        print src
        print dst
        # rename() function will 
        # rename all the files 
        os.rename(src, dst) 
  
# Driver Code 
if __name__ == '__main__': 
      
    # Calling main() function 
    main(inDirectory,outDirectory) 