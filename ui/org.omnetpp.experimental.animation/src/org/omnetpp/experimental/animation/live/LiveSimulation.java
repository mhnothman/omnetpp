package org.omnetpp.experimental.animation.live;

import org.omnetpp.experimental.animation.model.IRuntimeSimulation;
import org.omnetpp.experimental.animation.replay.RuntimeModule;

public class LiveSimulation implements IRuntimeSimulation {
	private RuntimeModule rootModule;
	private IEnvirCallback ev;
	private int eventNumber = -1;
	
	public LiveSimulation(IEnvirCallback ev) {
	    this.ev = ev;	
	}
	
	public RuntimeModule getRootModule() {
		return rootModule;
	}

	public RuntimeModule getModuleByID(String fullPath) {
		return null; //TODO
	}

	public RuntimeModule getModuleByPath(String fullPath) {
		return null; //TODO
	}

	public int getEventNumber() {
		return eventNumber;
	}
	
	public void doOneEvent() {
		switch (eventNumber) {
		case -1: // initialize
			ev.moduleCreated(null);
			ev.moduleCreated(null);
			ev.moduleCreated(null);
			break;
		case 0:
			ev.messageSent(null, null);
			break;
		case 1:
			ev.messageSent(null, null);
			break;
		case 2:
			break;
		case 3:
			break;
		case 4:
			break;
		}
		eventNumber++;
	}
}
