import javax.swing.filechooser.*;
import java.io.File;

public class PorcupineFileFilter extends FileFilter 
{

  String[] extensions;

  public PorcupineFileFilter(String ext) 
  {
	String[] exts = ext.split(",");
    extensions = new String[exts.length];
    for (int i = exts.length - 1; i >= 0; i--) {
      extensions[i] = exts[i].toLowerCase();
    }
  }

  public boolean accept(File f) {
    if (f.isDirectory()) 
	{ 
		return true; 
	}

    String name = f.getName().toLowerCase();
    for (int i = extensions.length - 1; i >= 0; i--) 
	{
      if (name.endsWith(extensions[i])) 
	  {
        return true;
      }
    }
    return false;
  }

  public String getDescription() 
  { 
	String desc = "Files of Type(";
	for (int i = extensions.length - 1; i >= 0; i--) 
	{
      desc += "*." + extensions[i].toLowerCase()+" ";
    }
	desc += ")";
	return desc; 
  }
}
