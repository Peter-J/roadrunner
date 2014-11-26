/* ----------------------------------------------------------------------------
 * This file was automatically generated by SWIG (http://www.swig.org).
 * Version 2.0.4
 *
 * Do not make changes to this file unless you know what you are doing--modify
 * the SWIG interface file instead.
 * ----------------------------------------------------------------------------- */

namespace libsbmlcs {

 using System;
 using System.Runtime.InteropServices;

/** 
 * @sbmlpackage{core}
 *
@htmlinclude pkg-marker-core.html Registry where package plug-ins are registered.
 *
 */

public class SBMLExtensionRegistry : IDisposable {
	private HandleRef swigCPtr;
	protected bool swigCMemOwn;
	
	internal SBMLExtensionRegistry(IntPtr cPtr, bool cMemoryOwn)
	{
		swigCMemOwn = cMemoryOwn;
		swigCPtr    = new HandleRef(this, cPtr);
	}
	
	internal static HandleRef getCPtr(SBMLExtensionRegistry obj)
	{
		return (obj == null) ? new HandleRef(null, IntPtr.Zero) : obj.swigCPtr;
	}
	
	internal static HandleRef getCPtrAndDisown (SBMLExtensionRegistry obj)
	{
		HandleRef ptr = new HandleRef(null, IntPtr.Zero);
		
		if (obj != null)
		{
			ptr             = obj.swigCPtr;
			obj.swigCMemOwn = false;
		}
		
		return ptr;
	}

  public virtual void Dispose() {
    lock(this) {
      if (swigCPtr.Handle != IntPtr.Zero) {
        if (swigCMemOwn) {
          swigCMemOwn = false;
          throw new MethodAccessException("C++ destructor does not have public access");
        }
        swigCPtr = new HandleRef(null, IntPtr.Zero);
      }
      GC.SuppressFinalize(this);
    }
  }

  
/**
   *
   * Returns an instance (singleton) of the SBMLExtensionRegistry class.
   * This function needs to be invoked when manipulating the SBMLExtensionRegistry class. 
   *
   * @return the instance of the SBMLExtensionRegistry object.
   */ public
 static SBMLExtensionRegistry getInstance() {
    SBMLExtensionRegistry ret = new SBMLExtensionRegistry(libsbmlPINVOKE.SBMLExtensionRegistry_getInstance(), false);
    return ret;
  }

  
/**
   * Add the given SBMLExtension to this SBMLExtensionRegistry.
   *
   * @param ext the SBMLExtension object to be added.
   *   
   * @return integer value indicating success/failure of the
   * function.  The possible values returned by this function are:
   * @li @link libsbmlcs#LIBSBML_OPERATION_SUCCESS LIBSBML_OPERATION_SUCCESS@endlink
   * @li @link libsbmlcs#LIBSBML_PKG_CONFLICT LIBSBML_PKG_CONFLICT@endlink
   * @li @link libsbmlcs#LIBSBML_INVALID_ATTRIBUTE_VALUE LIBSBML_INVALID_ATTRIBUTE_VALUE@endlink
   */ public
 int addExtension(SBMLExtension ext) {
    int ret = libsbmlPINVOKE.SBMLExtensionRegistry_addExtension(swigCPtr, SBMLExtension.getCPtr(ext));
    return ret;
  }

  
/**
   * Returns an SBMLExtension object with the given package URI or package name (string).
   *
   * @param package the URI or name of the package extension
   *
   * @return a clone of the SBMLExtension object with the given package URI or name. The returned 
   *         extension is to be freed (i.e.: deleted) by the caller!
   */ public
 SBMLExtension getExtension(string package) {
        SBMLExtension ret
	    = (SBMLExtension) libsbml.DowncastExtension(libsbmlPINVOKE.SBMLExtensionRegistry_getExtension(swigCPtr, package), false);
    if (libsbmlPINVOKE.SWIGPendingException.Pending) throw libsbmlPINVOKE.SWIGPendingException.Retrieve();
        return ret;
}

  
/**
   * Remove all L2 Extension namespaces from the namespace list. This will call all 
   * overriden SBMLExtension::removeL2Namespaces methods.
   */ public
 void removeL2Namespaces(XMLNamespaces xmlns) {
    libsbmlPINVOKE.SBMLExtensionRegistry_removeL2Namespaces(swigCPtr, XMLNamespaces.getCPtr(xmlns));
  }

  
/**
   * adds all L2 Extension namespaces to the namespace list. This will call all 
   * overriden SBMLExtension::addL2Namespaces methods.
   */ public
 void addL2Namespaces(XMLNamespaces xmlns) {
    libsbmlPINVOKE.SBMLExtensionRegistry_addL2Namespaces(swigCPtr, XMLNamespaces.getCPtr(xmlns));
  }

  
/**
   * Enables all extensions that support serialization / deserialization with
   * SBML Annotations.
   */ public
 void enableL2NamespaceForDocument(SBMLDocument doc) {
    libsbmlPINVOKE.SBMLExtensionRegistry_enableL2NamespaceForDocument(swigCPtr, SBMLDocument.getCPtr(doc));
  }

  
/** 
   * Goes through all extensions in the list of plugins of the given document
   * and disables all plugins that are not being used. 
   */ public
 void disableUnusedPackages(SBMLDocument doc) {
    libsbmlPINVOKE.SBMLExtensionRegistry_disableUnusedPackages(swigCPtr, SBMLDocument.getCPtr(doc));
  }

  
/**
   * Disables the package with the given URI / name.
   */ public
 static void disablePackage(string package) {
    libsbmlPINVOKE.SBMLExtensionRegistry_disablePackage(package);
    if (libsbmlPINVOKE.SWIGPendingException.Pending) throw libsbmlPINVOKE.SWIGPendingException.Retrieve();
  }

  
/**
   * If the given @p package is enabled, returns @c true; otherwise,
   * returns @c false.
   *
   * @return the status (enabled = <b>true</b>, disabled = <b>false</b> of the given package.
   */ public
 static bool isPackageEnabled(string package) {
    bool ret = libsbmlPINVOKE.SBMLExtensionRegistry_isPackageEnabled(package);
    if (libsbmlPINVOKE.SWIGPendingException.Pending) throw libsbmlPINVOKE.SWIGPendingException.Retrieve();
    return ret;
  }

  
/**
   * Enables the package with the given URI / name.
   */ public
 static void enablePackage(string package) {
    libsbmlPINVOKE.SBMLExtensionRegistry_enablePackage(package);
    if (libsbmlPINVOKE.SWIGPendingException.Pending) throw libsbmlPINVOKE.SWIGPendingException.Retrieve();
  }

  
/**
   * Returns the number of SBMLExtension with the given extension point.
   *
   * @param extPoint the SBaseExtensionPoint
   *
   * @return the number of SBMLExtension with the given extension point.
   */ public
 long getNumExtension(SBaseExtensionPoint extPoint) { return (long)libsbmlPINVOKE.SBMLExtensionRegistry_getNumExtension(swigCPtr, SBaseExtensionPoint.getCPtr(extPoint)); }

  
/**
   * Enable/disable the package with the given uri.
   *
   * @param uri the URI of the target package.
   * @param isEnabled the bool value corresponding to enabled (true) or 
   * disabled (false)
   *
   * @return false will be returned if the given bool value is false 
   * or the given package is not registered, otherwise true will be
   * returned.
   */ public
 bool setEnabled(string uri, bool isEnabled) {
    bool ret = libsbmlPINVOKE.SBMLExtensionRegistry_setEnabled(swigCPtr, uri, isEnabled);
    if (libsbmlPINVOKE.SWIGPendingException.Pending) throw libsbmlPINVOKE.SWIGPendingException.Retrieve();
    return ret;
  }

  
/**
   * Checks if the extension with the given URI is enabled (true) or 
   * disabled (false)
   *
   * @param uri the URI of the target package.
   *
   * @return false will be returned if the given package is disabled 
   * or not registered, otherwise true will be returned.
   */ public
 bool isEnabled(string uri) {
    bool ret = libsbmlPINVOKE.SBMLExtensionRegistry_isEnabled(swigCPtr, uri);
    if (libsbmlPINVOKE.SWIGPendingException.Pending) throw libsbmlPINVOKE.SWIGPendingException.Retrieve();
    return ret;
  }

  
/**
   * Checks if the extension with the given URI is registered (true) 
   * or not (false)
   *
   * @param uri the URI of the target package.
   *
   * @return true will be returned if the package with the given URI
   * is registered, otherwise false will be returned.
   */ public
 bool isRegistered(string uri) {
    bool ret = libsbmlPINVOKE.SBMLExtensionRegistry_isRegistered(swigCPtr, uri);
    if (libsbmlPINVOKE.SWIGPendingException.Pending) throw libsbmlPINVOKE.SWIGPendingException.Retrieve();
    return ret;
  }

  
/** 
   * Returns the number of registered packages.
   * 
   * @return the number of registered packages.
   */ public
 static long getNumRegisteredPackages() { return (long)libsbmlPINVOKE.SBMLExtensionRegistry_getNumRegisteredPackages(); }

  
/** 
   * Returns the registered package name at the given index
   * 
   * @param index zero based index of the package name to return
   * 
   * @return the package name with the given index or null
   */ public
 static string getRegisteredPackageName(long index) {
    string ret = libsbmlPINVOKE.SBMLExtensionRegistry_getRegisteredPackageName(index);
    return ret;
  }

}

}