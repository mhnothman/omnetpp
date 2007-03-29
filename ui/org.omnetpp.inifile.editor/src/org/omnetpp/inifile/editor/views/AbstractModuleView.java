package org.omnetpp.inifile.editor.views;

import org.eclipse.jface.viewers.ISelection;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.ui.IEditorPart;
import org.eclipse.ui.IPartListener;
import org.eclipse.ui.ISelectionListener;
import org.eclipse.ui.IWorkbenchPart;
import org.omnetpp.common.ui.ViewWithMessagePart;
import org.omnetpp.inifile.editor.InifileEditorPlugin;
import org.omnetpp.inifile.editor.editors.InifileSelectionItem;
import org.omnetpp.inifile.editor.model.IInifileDocument;
import org.omnetpp.inifile.editor.model.InifileUtils;
import org.omnetpp.inifile.editor.model.InifileUtils.Type;
import org.omnetpp.ned.model.NEDElement;
import org.omnetpp.ned.model.NEDTreeUtil;
import org.omnetpp.ned.model.interfaces.IModelProvider;
import org.omnetpp.ned.model.notification.INEDChangeListener;
import org.omnetpp.ned.model.notification.NEDModelEvent;
import org.omnetpp.ned.model.pojo.CompoundModuleNode;
import org.omnetpp.ned.model.pojo.SimpleModuleNode;
import org.omnetpp.ned.model.pojo.SubmoduleNode;
import org.omnetpp.ned.resources.NEDResourcesPlugin;

/**
 * Abstract base class for views that display information based on a single NED
 * module or network type, and possibly an inifile. Subclasses are expected to 
 * implement the buildContent() method, which will be invoked whenever the 
 * selection changes, or there is a change in NED or ini files.
 * 
 * @author Andras
 */
public abstract class AbstractModuleView extends ViewWithMessagePart {
	private ISelectionListener selectionChangedListener;
	private IPartListener partListener;
	private INEDChangeListener nedChangeListener;
	
	public AbstractModuleView() {
	}

	@Override
	public void createPartControl(Composite parent) {
		super.createPartControl(parent);
		hookListeners();
		scheduleRebuildContent();
	}

	@Override
	public void dispose() {
		unhookListeners();
		super.dispose();
	}

	protected void hookListeners() {
		// Listen on selection changes
		selectionChangedListener = new ISelectionListener() {
			public void selectionChanged(IWorkbenchPart part, ISelection selection) {
				workbenchSelectionChanged();
			}
		};
		getSite().getPage().addPostSelectionListener(selectionChangedListener);
		
		// Listens to workbench changes, and invokes activeEditorChanged() whenever the 
		// active editor changes. Listening on workbench changes is needed because 
		// editor don't always send selection changes when they get opened or closed.
		//
		// NOTE: the view only gets workbench events while it is visible. So we also
		// need to update our contents on getting activated.
		//
		final IEditorPart initialEditor = getActiveEditor();
		partListener = new IPartListener() {
			private IEditorPart activeEditor = initialEditor;
			
			public void partActivated(IWorkbenchPart part) {
				if (part == AbstractModuleView.this) {
					viewActivated();
				}
				if (part instanceof IEditorPart) {
					activeEditor = (IEditorPart) part;
					activeEditorChanged();
				}
			}

			public void partBroughtToTop(IWorkbenchPart part) {
			}

			public void partClosed(IWorkbenchPart part) {
				if (part == activeEditor) {
					activeEditor = null;
					activeEditorChanged();
				}
			}

			public void partDeactivated(IWorkbenchPart part) {
			}

			public void partOpened(IWorkbenchPart part) {
			}
		};
		getSite().getPage().addPartListener(partListener);
		
		// Listen on NED changes as well (note: inifile changes arrive as selection changes) 
		nedChangeListener = new INEDChangeListener() {
			public void modelChanged(NEDModelEvent event) {
				nedModelChanged();
			}
		};
		NEDResourcesPlugin.getNEDResources().getNEDModelChangeListenerList().add(nedChangeListener);
	}
	
	protected void unhookListeners() {
		if (selectionChangedListener != null)
			getSite().getPage().removePostSelectionListener(selectionChangedListener);
		if (partListener != null)
			getSite().getPage().removePartListener(partListener);
		if (nedChangeListener != null)
			NEDResourcesPlugin.getNEDResources().getNEDModelChangeListenerList().remove(nedChangeListener);
	}

	public void workbenchSelectionChanged() {
		System.out.println("*** SELECTIONCHANGE");
		scheduleRebuildContent();
	}

	protected void viewActivated() {
		System.out.println("*** VIEW ACTIVATED");
		scheduleRebuildContent();
	}

	protected void activeEditorChanged() {
		System.out.println("*** ACTIVE EDITOR CHANGED");
		scheduleRebuildContent();
	}

	protected void nedModelChanged() {
		System.out.println("*** NED MODEL CHANGE");
		scheduleRebuildContent();
	}

	public void scheduleRebuildContent() {
		rebuildContent();
		Display.getDefault().asyncExec(new Runnable() {
			public void run() {
				rebuildContent();
			}
		});
	}

	public void rebuildContent() {
		if (isDisposed())
			return;
		
		IEditorPart activeEditor = getActiveEditor();
		if (activeEditor==null) {
			displayMessage("There is no active editor.");
			return;
		}

		ISelection selection = getActiveEditorSelection();
		if (selection==null) {
			displayMessage("Nothing is selected.");
			return;
		}
		
		//System.out.println("SELECTION: "+selection);
		
		if (selection instanceof IStructuredSelection && !selection.isEmpty()) {
			Object element = ((IStructuredSelection)selection).getFirstElement();
			if (element instanceof IModelProvider) {
				//
				// The NED graphical editor publishes selection as an IStructuredSelection,
				// with editparts in it. NEDElement can be extracted from editparts
				// via IModelProvider.
				//
				Object model = ((IModelProvider)element).getModel();
				if (model instanceof CompoundModuleNode) {
					CompoundModuleNode node = (CompoundModuleNode)model;
					String moduleTypeName = node.getName();
					buildContent(moduleTypeName, null);
					hideMessage();
				}
				else if (model instanceof SimpleModuleNode) {
					SimpleModuleNode node = (SimpleModuleNode)model;
					String moduleTypeName = node.getName();
					buildContent(moduleTypeName, null);
					hideMessage();
				}
				else if (model instanceof SubmoduleNode) {
					SubmoduleNode submodule = (SubmoduleNode)model;
					String submoduleName = InifileUtils.getSubmoduleFullName(submodule);
					String submoduleType = InifileUtils.getSubmoduleType(submodule);
					buildContent(submoduleName, submoduleType, null);
					hideMessage();
				}
			}
			else if (element instanceof InifileSelectionItem) {
				//
				// The inifile editor publishes selection in InifileSelectionItems.
				//
				InifileSelectionItem sel = (InifileSelectionItem) element;
				IInifileDocument doc = sel.getDocument();
				String section = sel.getSection();

				String networkName = doc.getValue("General", "network"); //XXX or [Run X], if that's the selected one!
				if (networkName == null) {
					displayMessage("Network not specified (no [General]/network= setting)");
					return;
				}
				buildContent(networkName, doc);
				hideMessage();
			}
			
		}
		else {
			displayMessage("Please open an inifile or NED editor.");
		}
	}

	/**
	 * Delegates to the other buildContent() method. 
	 */
	protected void buildContent(String moduleTypeName, IInifileDocument doc) {
		buildContent(moduleTypeName, moduleTypeName, doc);
	}

	/**
	 * Update view to display content that corresponds to the given module, 
	 * with the specified inifile as configuration. 
	 */
	protected abstract void buildContent(String submoduleName, String submoduleType, IInifileDocument doc);


	/* stuff for subclasses: icons */
	public static final String ICON_ERROR = "icons/full/obj16/Error.png";
	public static final String ICON_UNASSIGNEDPAR = "icons/full/obj16/UnassignedPar.png";
	public static final String ICON_NEDPAR = "icons/full/obj16/NedPar.png";
	public static final String ICON_INIPAR = "icons/full/obj16/IniPar.png";
	public static final String ICON_INIPARREDUNDANT = "icons/full/obj16/IniParRedundant.png";
	
	/**
	 * Helper function: suggests an icon for a table or tree entry.
	 */
	protected static Image suggestImage(Type type, NEDElement element) {
		switch (type) {
			case ERROR: return InifileEditorPlugin.getImage(ICON_ERROR);
			case UNASSIGNED_PAR: return InifileEditorPlugin.getImage(ICON_UNASSIGNEDPAR);
			case NED_PAR: return InifileEditorPlugin.getImage(ICON_NEDPAR);
			case INI_PAR: return InifileEditorPlugin.getImage(ICON_INIPAR);
			case INI_PAR_REDUNDANT: return InifileEditorPlugin.getImage(ICON_INIPARREDUNDANT);
			case OTHER: if (element!=null) return NEDTreeUtil.getNedModelLabelProvider().getImage(element);
		}
		return null;
	}
}
