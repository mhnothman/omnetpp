#ifndef _JMESSAGE_H_
#define _JMESSAGE_H_

#include <jni.h>
#include <stdio.h>
#include <assert.h>
#include <omnetpp.h>

/**
 * Implements a message class that can be extended in Java
 */
class JMessage : public cMessage
{
  protected:
    jobject javaPeer;
    jmethodID cloneMethod;

  protected:
    void checkExceptions() const;

  public:
    explicit JMessage(const char *name, int kind, int dummy);
    JMessage(const JMessage& msg);
    virtual ~JMessage();
    JMessage& operator=(const JMessage& msg);
    virtual cPolymorphic *dup() const  {return new JMessage(*this);}
    void swigSetJavaPeer(jobject msgObject);
    jobject swigJavaPeer() {return javaPeer;}
    static jobject swigJavaPeerOf(cObject *object);

    int getIntJavaField(const char *fieldName) const;
    void setIntJavaField(const char *fieldName, int value);
    ...
    // info() should return Java's toString()
};

#endif


