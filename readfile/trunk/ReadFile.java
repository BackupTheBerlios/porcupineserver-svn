import java.applet.*; 
import java.io.*;
import java.security.*;
import java.util.Hashtable;
import java.util.Iterator;

import javax.swing.JFileChooser;

//import sun.applet.AppletIllegalArgumentException;

public class ReadFile extends Applet { 
	Hashtable _files = new Hashtable();
	int _file_id = 0;
	public boolean Compress = false;
	public int ChunkSize = 32768;
	//-------------------------------------------------------- 
	public void init() {
	  	String param = null;
/*
	  	int fileno = 0;
		param = getParameter("File"); 
		if ( param != null) {
			try {
				fileno = this.setFile(param);
			}
			catch (FileNotFoundException e) {
				throw new AppletIllegalArgumentException(e.getMessage());
			}
		}
*/
		// Get setup parameters from applet html
		param = getParameter("ChunkSize");
		if (param!=null) ChunkSize = Integer.parseInt(param);
		param = getParameter("Compress");
		if (param!=null && Integer.parseInt(param)==1) Compress = true;

		//Boolean s = saveFile("test.oql", "ssss");
		//this.destroy();
/*	
		try {
		getChunk(fileno);
		getChunk(fileno);
		getChunk(fileno);
		getChunk(fileno);
		getChunk(fileno);
		getChunk(fileno);
		} catch (IOException e) {}
*/
	}
//--------------------------------------------------------
	public int setFile(String filename) throws FileNotFoundException {
	  	FileInfo fileinf = new FileInfo(filename);
	  	int retVal = _file_id;
	  	_files.put(new Integer(_file_id), fileinf);
	  	_file_id++;
	  	return(retVal);
	}
//--------------------------------------------------------
	public long getFileSize(int fileno) {
		FileInfo fileinf = (FileInfo)_files.get(new Integer(fileno));
		return(fileinf.getFileSize());
	}
//--------------------------------------------------------
	public long getBytesRead(int fileno) {
		FileInfo fileinf = (FileInfo)_files.get(new Integer(fileno));
		return(fileinf.BytesRead);
	}
//--------------------------------------------------------
	public String getChunk(int fileno) throws IOException {
		Integer key = new Integer(fileno);
		FileInfo fileinf = (FileInfo)_files.get(key);
		String chunk = fileinf.getChunk();
		if (chunk==null)
			_files.remove(key);
		return (chunk);
	}
//--------------------------------------------------------
	public void closeFile(int fileno) {
		Integer key = new Integer(fileno);
		FileInfo fileinf = (FileInfo)_files.get(key);
		try {
			fileinf.discard();
		} catch (IOException e) {}
		_files.remove(key);
	}
//--------------------------------------------------------
	public void destroy() {
		FileInfo fileinf = null;
		Iterator files = _files.values().iterator();
		while (files.hasNext()){
			fileinf = (FileInfo)files.next();
			try {
				fileinf.discard();
			} catch ( IOException e) {}
		}
	}
//--------------------------------------------------------
	public String selectFiles(final boolean multiselect) {
		final Applet applet = this;
		String selection = "";
		
		try {
		    selection = ( String )AccessController.doPrivileged(
		            new PrivilegedExceptionAction() {
		            public Object run() {
		             	JFileChooser fileChooser = new JFileChooser();
		             	File[] files;
		             	String selection = "";
		             	fileChooser.setMultiSelectionEnabled(multiselect);
		
		             	
		             	int ret = 0;
		             	ret = fileChooser.showDialog(applet, "Upload");                	
		
		                if(ret == JFileChooser.APPROVE_OPTION) {
		                	if (!multiselect)
		                		selection = fileChooser.getSelectedFile().getPath();
		                	else {
		                		files = fileChooser.getSelectedFiles();
		                		for (int i=0; i<files.length; i++) {
		                			selection += files[i].getPath() + ";";
		                		}
		                	}
		                }
		                return(selection);
		            }
		        }
		    );
		}
		catch ( PrivilegedActionException e ) { }
		
		return selection;
	}
//	--------------------------------------------------------
	public Boolean saveFile(final String fname, final String text) {
		final Applet applet = this;
		Boolean success= new Boolean(false);
		
		try {
		    success = ( Boolean )AccessController.doPrivileged(
		            new PrivilegedExceptionAction() {
		            public Object run() {
		             	JFileChooser fileChooser = new JFileChooser();
		             	FileWriter fileWriter;
		             	String selection = "";

		             	fileChooser.setSelectedFile(new File(fname));
		             	
		             	int ret = 0;
		             	ret = fileChooser.showSaveDialog(applet);
		
		                if(ret == JFileChooser.APPROVE_OPTION) {
	                		selection = fileChooser.getSelectedFile().getPath();
	                		//File new_file = new File(selection);
	                		try {
	                			fileWriter = new FileWriter(selection);
	                			fileWriter.write(text);
	                			fileWriter.close();
	                		}
	                		catch (IOException e) {
	                			return(new Boolean(false));
	                		}
		                }
		                return(new Boolean(true));
		            }
		        }
		    );
		}
		catch ( PrivilegedActionException e ) { }
		
		return success;
	}
//--------------------------------------------------------
	private class FileInfo {
		FileInputStream in = null;
	    long filesize = 0;
	    boolean _finished_reading = false;
	    public long BytesRead = 0;
	    //--------------------------------------------------------
	 	public FileInfo(final String filename) throws FileNotFoundException {
	 		try {
	 	        in = ( FileInputStream )AccessController.doPrivileged(
	 	                new PrivilegedExceptionAction() {
	 	                public Object run() throws FileNotFoundException {
	 	                	File file = new File(filename);
	 	                	
	 	                    filesize = file.length();
	 	                    BytesRead = 0;
	 	                    _finished_reading = false;
	 	                    return new FileInputStream( file );
	 	                }
	 	            }
	 	        );
	 		}
	 	    catch ( PrivilegedActionException e ) {
	 	        throw ( FileNotFoundException )e.getException();
	 	    }
	 	}
	 	//--------------------------------------------------------
		public long getFileSize() {
			return(filesize);
		}
		//--------------------------------------------------------
		public void discard () throws IOException {
			in.close();
			in = null;
		}
		//--------------------------------------------------------
		public String getChunk() throws IOException {
		  	int bytes_read = -1;
		  	byte [] cbuf = new byte [ChunkSize];
		  	String b64 = null;
		  	
		  	if ( in!=null && !_finished_reading ) {
				bytes_read = in.read(cbuf, 0, ChunkSize);
			
				if (bytes_read != -1) {
			  		// use gzip compression...
			  		BytesRead += bytes_read;
			  		if (Compress)
			  			b64 = Base64.encodeBytes(cbuf, 0, bytes_read, Base64.GZIP);
			  		else
			  			b64 = Base64.encodeBytes(cbuf, 0, bytes_read, Base64.NO_OPTIONS);
			  	}
			  	else {
			  		// eof - return empty string
			  		this.discard();
			  		_finished_reading = true;
			  	}
		  	}
		  	return (b64); 
		}
	}
}